from rest_framework import serializers
from .models import AnalysisTask, ChartConfig


class AnalysisTaskSerializer(serializers.ModelSerializer):
    dataset_name = serializers.SerializerMethodField()
    columns = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisTask
        fields = (
            'id', 'user', 'dataset', 'dataset_name', 'columns',
            'task_type', 'parameters', 'result_data', 'metrics',
            'status', 'created_at',
        )
        read_only_fields = ('id', 'user', 'status', 'created_at')

    def get_dataset_name(self, obj):
        return obj.dataset.name

    def get_columns(self, obj):
        return obj.dataset.columns


class AnalysisTaskListSerializer(serializers.ModelSerializer):
    dataset_name = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisTask
        fields = (
            'id', 'dataset', 'dataset_name', 'task_type',
            'parameters', 'metrics', 'status', 'created_at',
        )

    def get_dataset_name(self, obj):
        return obj.dataset.name


class ChartConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChartConfig
        fields = ('id', 'user', 'analysis_task', 'chart_type', 'config', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
