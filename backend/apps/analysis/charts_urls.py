from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.ChartGenerateView.as_view(), name='chart_generate'),
    path('configs/', views.ChartConfigListView.as_view(), name='chart_configs'),
]
