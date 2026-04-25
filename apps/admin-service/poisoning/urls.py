from django.urls import path
from . import views

urlpatterns = [
    path('', views.poisoning_list, name='poisoning-list'),
    path('<str:event_id>/', views.poisoning_detail, name='poisoning-detail'),
]
