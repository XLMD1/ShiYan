import os

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response

from django.conf import settings

from .models import AnalysisTask, ChartConfig
from .serializers import (
    AnalysisTaskSerializer,
    AnalysisTaskListSerializer,
    ChartConfigSerializer,
)
from .cleaning import clean_dataset, get_column_stats
from .clustering import run_kmeans
from .regression import run_regression
from .visualization import build_echarts_option
from apps.datafile.models import Dataset


def _get_dataset_or_404(user, dataset_id):
    """获取用户的数据集，不存在则返回 404"""
    try:
        return Dataset.objects.get(id=dataset_id, user=user)
    except Dataset.DoesNotExist:
        return None


def _read_dataframe(file_path):
    """读取 CSV/Excel 文件，返回 DataFrame"""
    import pandas as pd
    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    else:
        return pd.read_excel(file_path)


# ---------- Analysis Tasks ----------

class AnalysisTaskListView(generics.ListAPIView):
    """分析历史记录列表"""
    serializer_class = AnalysisTaskListSerializer

    def get_queryset(self):
        qs = AnalysisTask.objects.filter(user=self.request.user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs.order_by('-created_at')


class AnalysisTaskDetailView(generics.RetrieveAPIView):
    """单次分析详情"""
    serializer_class = AnalysisTaskSerializer

    def get_queryset(self):
        return AnalysisTask.objects.filter(user=self.request.user)


# ---------- Data Cleaning ----------

class StatsView(APIView):
    """数据概览统计"""

    def get(self, request, dataset_id):
        import pandas as pd

        dataset = _get_dataset_or_404(request.user, dataset_id)
        if dataset is None:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)

        try:
            df = _read_dataframe(dataset.cleaned_file_path)
        except Exception as e:
            return Response({'error': f'读取文件失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        columns_info = []
        total_missing = 0
        total_outliers = 0

        for col in df.columns:
            col_stats = get_column_stats(df, col)
            col_type = 'numeric' if pd.api.types.is_numeric_dtype(df[col]) else 'string'
            col_info = {
                'name': str(col),
                'type': col_type,
                **col_stats,
            }
            columns_info.append(col_info)
            total_missing += col_stats.get('missing', 0)
            if col_type == 'numeric':
                total_outliers += col_stats.get('outliers_iqr', 0)

        return Response({
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'total_missing': total_missing,
            'total_outliers': total_outliers,
            'columns': columns_info,
        })


class CleanView(APIView):
    """执行数据清洗"""

    def post(self, request, dataset_id):
        dataset = _get_dataset_or_404(request.user, dataset_id)
        if dataset is None:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)

        cleaning_config = request.data or {}
        columns_config = cleaning_config.get('columns', [])

        if not columns_config:
            return Response({'error': '请指定至少一列的清洗方式'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cleaned_df, report = clean_dataset(dataset.file.path, cleaning_config)
        except Exception as e:
            return Response({'error': f'清洗失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # 保存清洗后的文件（覆盖原文件或新建文件）
        original_path = dataset.file.path
        base, ext = os.path.splitext(original_path)
        cleaned_path = f'{base}_cleaned{ext}'

        if ext.lower() == '.csv':
            cleaned_df.to_csv(cleaned_path, index=False)
        else:
            cleaned_df.to_excel(cleaned_path, index=False)

        # 更新数据集记录
        dataset.is_cleaned = True
        dataset.rows = len(cleaned_df)
        dataset.save(update_fields=['is_cleaned', 'rows'])

        return Response({
            'report': report,
            'rows': len(cleaned_df),
            'columns': list(cleaned_df.columns),
            'is_cleaned': True,
        })


# ---------- Analysis Algorithms ----------

class KMeansView(APIView):
    """执行 K-Means 聚类"""

    def post(self, request):
        dataset_id = request.data.get('dataset_id')
        features = request.data.get('features', [])
        k = request.data.get('k', 3)

        if not dataset_id:
            return Response({'error': '请提供 dataset_id'}, status=status.HTTP_400_BAD_REQUEST)

        dataset = _get_dataset_or_404(request.user, dataset_id)
        if dataset is None:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not features or len(features) < 1:
            return Response({'error': '请至少选择一个特征列'}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(k, int) or k < 2 or k > 10:
            return Response({'error': 'K 值必须在 2~10 之间'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = run_kmeans(dataset.cleaned_file_path, features, k)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'K-Means 聚类失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        task = AnalysisTask.objects.create(
            user=request.user,
            dataset=dataset,
            task_type='kmeans',
            parameters={'features': features, 'k': k},
            result_data=result.get('result_data', []),
            metrics=result.get('metrics', {}),
            status='done',
        )

        serializer = AnalysisTaskSerializer(task)
        return Response({
            'task': serializer.data,
            'cluster_labels': result.get('cluster_labels', []),
            'cluster_centers': result.get('cluster_centers', {}),
            'cluster_sizes': result.get('cluster_sizes', {}),
            'metrics': result.get('metrics', {}),
        }, status=status.HTTP_201_CREATED)


class RegressionView(APIView):
    """执行线性回归"""

    def post(self, request):
        dataset_id = request.data.get('dataset_id')
        x_columns = request.data.get('x_columns', [])
        y_column = request.data.get('y_column')

        if not dataset_id:
            return Response({'error': '请提供 dataset_id'}, status=status.HTTP_400_BAD_REQUEST)

        dataset = _get_dataset_or_404(request.user, dataset_id)
        if dataset is None:
            return Response({'error': '数据集不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not x_columns or len(x_columns) < 1:
            return Response({'error': '请至少选择一个自变量 X'}, status=status.HTTP_400_BAD_REQUEST)

        if not y_column:
            return Response({'error': '请选择因变量 Y'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = run_regression(dataset.cleaned_file_path, x_columns, y_column)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'线性回归失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        task = AnalysisTask.objects.create(
            user=request.user,
            dataset=dataset,
            task_type='regression',
            parameters={'x_columns': x_columns, 'y_column': y_column},
            result_data=result.get('result_data', []),
            metrics=result.get('metrics', {}),
            status='done',
        )

        serializer = AnalysisTaskSerializer(task)
        return Response({
            'task': serializer.data,
            'metrics': result.get('metrics', {}),
        }, status=status.HTTP_201_CREATED)


# ---------- Charts ----------

class ChartGenerateView(APIView):
    """生成 ECharts 图表 option"""

    def post(self, request):
        chart_type = request.data.get('chart_type')
        data = request.data.get('data', {})
        config = request.data.get('config', {})

        if not chart_type:
            return Response({'error': '请提供图表类型'}, status=status.HTTP_400_BAD_REQUEST)

        valid_types = {'scatter', 'line', 'bar', 'heatmap', 'boxplot', 'pie'}
        if chart_type not in valid_types:
            return Response(
                {'error': f'不支持的图表类型: {chart_type}，支持: {", ".join(sorted(valid_types))}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            option = build_echarts_option(chart_type, data, config)
        except Exception as e:
            return Response({'error': f'图表生成失败: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # 如果传了 task_id，保存图表配置
        chart_id = None
        task_id = config.get('task_id')
        if task_id:
            try:
                task = AnalysisTask.objects.get(id=task_id, user=request.user)
                chart_config = ChartConfig.objects.create(
                    user=request.user,
                    analysis_task=task,
                    chart_type=chart_type,
                    config=config,
                )
                chart_id = chart_config.id
            except AnalysisTask.DoesNotExist:
                pass

        return Response({
            'option': option,
            'chart_id': chart_id,
        })


class ChartConfigListView(generics.ListAPIView):
    """用户保存的图表配置列表"""
    serializer_class = ChartConfigSerializer

    def get_queryset(self):
        return ChartConfig.objects.filter(user=self.request.user).order_by('-created_at')
