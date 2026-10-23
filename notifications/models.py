from django.db import models
from accounts.models import User

class Notification(models.Model):
    TYPE_CHOICES = (
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('SUCCESS', 'Success'),
        ('DANGER', 'Danger'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='INFO')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
