import os
import pandas as pd
from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Dataset
from .serializers import DatasetSerializer, DatasetListSerializer


class DatasetUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': '请选择要上传的文件'}, status=status.HTTP_400_BAD_REQUEST)

        filename = file_obj.name
        ext = os.path.splitext(filename)[1].lower()

        if ext == '.csv':
            file_type = 'csv'
            try:
                df = pd.read_csv(file_obj)
            except Exception:
                return Response({'error': 'CSV 文件解析失败'}, status=status.HTTP_400_BAD_REQUEST)
        elif ext in ('.xlsx', '.xls'):
            file_type = 'xlsx'
            try:
                df = pd.read_excel(file_obj)
            except Exception:
                return Response({'error': 'Excel 文件解析失败'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': '不支持的文件格式，请上传 CSV 或 Excel 文件'}, status=status.HTTP_400_BAD_REQUEST)

        file_obj.seek(0)

        dataset = Dataset.objects.create(
            user=request.user,
            name=filename,
            file=file_obj,
            file_type=file_type,
            rows=len(df),
            columns=list(df.columns),
        )

        return Response(DatasetSerializer(dataset).data, status=status.HTTP_201_CREATED)


class DatasetListView(ListAPIView):
    serializer_class = DatasetListSerializer

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)


class DatasetDetailView(RetrieveAPIView):
    serializer_class = DatasetSerializer

    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)


class DatasetPreviewView(APIView):
    def get(self, request, pk):
        try:
            dataset = Dataset.objects.get(id=pk, user=request.user)
        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)

        try:
            file_path = dataset.file.path
            if dataset.file_type == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
        except Exception as e:
            error_msg = f'文件读取失败: {str(e)}'
            return Response({'error': error_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 100))
        total = len(df)

        start = (page - 1) * page_size
        end = start + page_size
        page_data = df.iloc[start:end]
        
        rows = page_data.values.tolist()
        rows = [[None if pd.isna(cell) else cell for cell in row] for row in rows]

        return Response({
            'columns': list(df.columns),
            'rows': rows,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size,
        })


class DatasetDeleteView(DestroyAPIView):
    def get_queryset(self):
        return Dataset.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.file:
            if os.path.isfile(instance.file.path):
                os.remove(instance.file.path)
        instance.delete()


class URLTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            return result
        token = request.query_params.get('token')
        if not token:
            return None
        try:
            validated_token = self.get_validated_token(token.encode('utf-8'))
            user = self.get_user(validated_token)
            return (user, validated_token)
        except Exception:
            return None


class DatasetExportView(APIView):
    authentication_classes = [URLTokenAuthentication]

    def get(self, request, pk):
        try:
            dataset = Dataset.objects.get(id=pk, user=request.user)
        except Dataset.DoesNotExist:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)

        try:
            if dataset.file_type == 'csv':
                df = pd.read_csv(dataset.file.path)
            else:
                df = pd.read_excel(dataset.file.path)
        except Exception:
            return Response({'error': '文件读取失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        format_type = request.query_params.get('file_type', 'csv')
        base_name = os.path.splitext(dataset.name)[0]
        if dataset.is_cleaned:
            base_name = f'{base_name}_cleaned'

        if format_type == 'xlsx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename="{base_name}.xlsx"'
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            return response
        else:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{base_name}.csv"'
            response.charset = 'utf-8-sig'
            df.to_csv(path_or_buf=response, index=False)
            return response
