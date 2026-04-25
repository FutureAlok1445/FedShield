from django.urls import path
from . import views

urlpatterns = [
    path('', views.round_list, name='round-list'),
    path('<str:round_id>/', views.round_detail, name='round-detail'),
    path('start/', views.round_start, name='round-start'),
]
