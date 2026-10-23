from django.urls import path
from . import views

urlpatterns = [
    path('passport/', views.skill_passport, name='skill_passport'),
    path('roadmap/', views.career_roadmap, name='career_roadmap'),
]
