from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/', include('accounts.urls')),
    path('assessment/', include('assessment.urls')),
    path('career/', include('career.urls')),
    path('opportunities/', include('opportunities.urls')),
    path('analytics/', include('analytics.urls')),
    path('resume/', include('resume.urls')),
    path('interview/', include('interview.urls')),
    path('notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
