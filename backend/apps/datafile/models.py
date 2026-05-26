from django.db import models
from django.contrib.auth.models import User


class Dataset(models.Model):
    FILE_TYPE_CHOICES = [
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    rows = models.IntegerField(default=0)
    columns = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_cleaned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name
