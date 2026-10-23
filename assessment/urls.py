from django.urls import path
from . import views

urlpatterns = [
    path('', views.assessment_list, name='assessments'),
    path('<int:assessment_id>/take/', views.take_assessment, name='take_assessment'),
    path('result/<int:attempt_id>/', views.assessment_result, name='assessment_result'),
    path('task/<int:task_id>/complete/', views.complete_task, name='complete_task'),
]
