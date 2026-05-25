from django.urls import path
from . import views

urlpatterns = [
    path('tasks/', views.AnalysisTaskListView.as_view(), name='task_list'),
]
