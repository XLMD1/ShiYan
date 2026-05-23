from rest_framework import serializers
from .models import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ('id', 'user', 'name', 'file', 'file_type', 'rows', 'columns', 'uploaded_at', 'is_cleaned')
        read_only_fields = ('id', 'user', 'rows', 'columns', 'uploaded_at', 'is_cleaned')


class DatasetListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ('id', 'name', 'file_type', 'rows', 'columns', 'uploaded_at', 'is_cleaned')