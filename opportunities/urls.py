from django.urls import path
from . import views

urlpatterns = [
    path('hub/', views.opportunity_hub, name='opportunity_hub'),
]
