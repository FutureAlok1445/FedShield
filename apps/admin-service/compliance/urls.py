from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='compliance-report-list'),
    path('generate/', views.generate_report, name='compliance-generate-report'),
    path('<str:report_id>/download/', views.download_report, name='compliance-download-report'),
]
