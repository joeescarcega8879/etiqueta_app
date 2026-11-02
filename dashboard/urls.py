from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.dashboard_health, name='dashboard_health'),
]