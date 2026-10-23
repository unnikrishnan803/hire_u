from django.urls import path
from . import views

urlpatterns = [
    path('officer/dashboard/', views.officer_dashboard, name='officer_dashboard'),
]
