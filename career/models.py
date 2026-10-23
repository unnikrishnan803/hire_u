from django.db import models
from accounts.models import StudentProfile

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, blank=True, null=True) # e.g., Aptitude, Technical, Soft Skill
    
    def __str__(self):
        return self.name

class SkillProfile(models.Model):
    LEVEL_CHOICES = (
        ('BEGINNER', 'Beginner'),
        ('NORMAL', 'Normal'),
        ('ADVANCED', 'Advanced'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='BEGINNER')
    mastery_percentage = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    trend = models.CharField(max_length=20, default='Stable') # Improving, Stable, Declining
    
    class Meta:
        unique_together = ('student', 'skill')
        
    def __str__(self):
        return f"{self.student.user.username} - {self.skill.name}: {self.level}"
