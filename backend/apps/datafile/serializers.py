from rest_framework import serializers
from .models import Dataset


def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


class DatasetSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = ('id', 'user', 'name', 'file', 'file_type', 'rows', 'columns', 'uploaded_at', 'is_cleaned', 'file_size')
        read_only_fields = ('id', 'user', 'rows', 'columns', 'uploaded_at', 'is_cleaned', 'file_size')

    def get_file_size(self, obj):
        if obj.file and obj.file.size:
            return format_file_size(obj.file.size)
        return None


class DatasetListSerializer(serializers.ModelSerializer):
    file_size = serializers.SerializerMethodField()

    class Meta:
        model = Dataset
        fields = ('id', 'name', 'file_type', 'rows', 'columns', 'uploaded_at', 'is_cleaned', 'file_size')

    def get_file_size(self, obj):
        if obj.file and obj.file.size:
            return format_file_size(obj.file.size)
        return None