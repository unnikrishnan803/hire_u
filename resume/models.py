from django.db import models
from accounts.models import User

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Resume"

class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='analysis')
    ats_score = models.IntegerField(default=0)
    missing_keywords = models.TextField(blank=True, null=True) # Comma separated
    skill_gaps = models.TextField(blank=True, null=True)
    suggestions = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.resume.user.username} (Score: {self.ats_score})"
