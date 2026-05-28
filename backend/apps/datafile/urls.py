from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.DatasetUploadView.as_view(), name='dataset_upload'),
    path('', views.DatasetListView.as_view(), name='dataset_list'),
    path('<int:pk>/', views.DatasetDetailView.as_view(), name='dataset_detail'),
    path('<int:pk>/preview/', views.DatasetPreviewView.as_view(), name='dataset_preview'),
    path('<int:pk>/delete/', views.DatasetDeleteView.as_view(), name='dataset_delete'),
    path('<int:pk>/export/', views.DatasetExportView.as_view(), name='dataset_export'),
    path('fetch/', views.DataFetchView.as_view(), name='data_fetch'),
]