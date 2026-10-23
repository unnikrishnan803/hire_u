from django.db import models
from accounts.models import User, CareerTrack, Department

class Assessment(models.Model):
    ASSESSMENT_TYPES = (
        ('APTITUDE', 'Aptitude'),
        ('TECHNICAL', 'Technical Problem Solving'),
        ('COMMUNICATION', 'Communication & Interview'),
    )
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ASSESSMENT_TYPES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"

class AssessmentSection(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='sections')
    name = models.CharField(max_length=255) # e.g., Quantitative Aptitude, Logical Reasoning
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.assessment.title} - {self.name}"

class Question(models.Model):
    DIFFICULTY_CHOICES = (
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    )
    section = models.ForeignKey(AssessmentSection, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    
    # Specific filtering fields
    career_track = models.ForeignKey(CareerTrack, on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Simple MCQ for MVP
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=(('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')))
    
    explanation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Q: {self.text[:50]}..."

class AssessmentAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_attempts')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.assessment.title} Score: {self.score}"

class Answer(models.Model):
    attempt = models.ForeignKey(AssessmentAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Ans for {self.question.id} by {self.attempt.user.username}"
