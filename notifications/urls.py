from django.urls import path
from django.http import JsonResponse
from notifications.models import Notification
from django.contrib.auth.decorators import login_required

@login_required
def unread_count(request):
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})

urlpatterns = [
    path('unread-count/', unread_count, name='notif_count'),
]
