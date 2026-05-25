from django.db import models
from django.contrib.auth.models import User


class AnalysisTask(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dataset = models.ForeignKey('datafile.Dataset', on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20)
    parameters = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict, null=True, blank=True)
    metrics = models.JSONField(default=dict, null=True, blank=True)
    status = models.CharField(max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class ChartConfig(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    analysis_task = models.ForeignKey(AnalysisTask, on_delete=models.CASCADE, null=True, blank=True)
    chart_type = models.CharField(max_length=20)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
