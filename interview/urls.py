from django.urls import path
from . import views

urlpatterns = [
    path('mock/', views.mock_interview, name='mock_interview'),
    path('start/<str:mode>/', views.start_interview, name='start_interview'),
    path('session/<int:session_id>/', views.interview_question, name='interview_question'),
    path('session/<int:session_id>/result/', views.interview_result, name='interview_result'),
    path('coding/', views.coding_progress, name='coding_progress'),
]
