from django.db import models
from accounts.models import StudentProfile

class Badge(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, default='bi-award')  # Bootstrap icon class

    def __str__(self):
        return self.name

class StudentBadge(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'badge')

class Gamification(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE, related_name='gamification')
    xp = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.user.username} - XP: {self.xp}"
