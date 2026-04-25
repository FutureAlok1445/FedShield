from django.urls import path

from . import views

urlpatterns = [
    path('', views.audit_list, name='audit-list'),
    path('<str:entry_id>/', views.audit_detail, name='audit-detail'),
]
