from django.urls import path
from . import views

urlpatterns = [
    path('', views.bank_list, name='bank-list'),
    path('<str:bank_id>/', views.bank_detail, name='bank-detail'),
    path('<str:bank_id>/status/', views.bank_status_update, name='bank-status-update'),
    path('<str:bank_id>/compliance/', views.bank_compliance, name='bank-compliance'),
]
