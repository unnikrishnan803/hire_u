from django.db import models
from accounts.models import StudentProfile

class DailyTask(models.Model):
    DIFFICULTY_CHOICES = (('EASY', 'Easy'), ('MEDIUM', 'Medium'), ('HARD', 'Hard'))
    STATUS_CHOICES = (('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('SKIPPED', 'Skipped'))

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='daily_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    skill_area = models.CharField(max_length=100, blank=True, null=True)  # e.g., DSA, SQL
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    estimated_minutes = models.IntegerField(default=15)
    xp_reward = models.IntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} - {self.title} ({self.date})"

class LearningContent(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('ARTICLE', 'Article'),
        ('VIDEO', 'Video'),
        ('QUIZ', 'Quiz'),
        ('EXERCISE', 'Exercise'),
    )
    title = models.CharField(max_length=255)
    topic = models.CharField(max_length=100)
    skill_area = models.CharField(max_length=100)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    content = models.TextField()
    difficulty = models.CharField(max_length=10, default='MEDIUM')
    estimated_minutes = models.IntegerField(default=10)
    xp_reward = models.IntegerField(default=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
