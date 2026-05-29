from django.urls import path
from . import views

urlpatterns = [
    # 分析任务
    path('tasks/', views.AnalysisTaskListView.as_view(), name='task_list'),
    path('tasks/<int:pk>/', views.AnalysisTaskDetailView.as_view(), name='task_detail'),

    # 数据清洗
    path('clean/<int:dataset_id>/', views.CleanView.as_view(), name='clean'),
    path('stats/<int:dataset_id>/', views.StatsView.as_view(), name='stats'),
    path('reset/<int:dataset_id>/', views.ResetView.as_view(), name='reset'),

    # 分析算法
    path('kmeans/', views.KMeansView.as_view(), name='kmeans'),
    path('regression/', views.RegressionView.as_view(), name='regression'),

    # 图表
    path('charts/generate/', views.ChartGenerateView.as_view(), name='charts_generate'),
    path('charts/configs/', views.ChartConfigListView.as_view(), name='charts_configs'),
]
