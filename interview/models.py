from django.db import models
from accounts.models import User

class InterviewSession(models.Model):
    MODE_CHOICES = (
        ('HR', 'HR Interview'),
        ('TECHNICAL', 'Technical Interview'),
        ('COMPANY', 'Company Interview'),
    )
    STATUS_CHOICES = (('ACTIVE', 'Active'), ('COMPLETED', 'Completed'))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default='HR')
    overall_score = models.IntegerField(default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    strengths = models.TextField(blank=True, null=True)
    weaknesses = models.TextField(blank=True, null=True)
    recommendations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mode} ({self.status})"

class InterviewQuestion(models.Model):
    mode = models.CharField(max_length=20)
    question_text = models.TextField()
    ideal_answer_points = models.TextField(blank=True, null=True)  # Key points expected
    skill_area = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.CharField(max_length=10, default='MEDIUM')

    def __str__(self):
        return f"[{self.mode}] {self.question_text[:60]}..."

class InterviewAnswer(models.Model):
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE)
    student_answer = models.TextField()
    score_technical = models.IntegerField(default=0)   # /40
    score_relevance = models.IntegerField(default=0)    # /20
    score_explanation = models.IntegerField(default=0)  # /20
    score_communication = models.IntegerField(default=0) # /10
    score_completeness = models.IntegerField(default=0)  # /10
    feedback = models.TextField(blank=True, null=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_score(self):
        return (self.score_technical + self.score_relevance +
                self.score_explanation + self.score_communication + self.score_completeness)

    def __str__(self):
        return f"Answer by {self.session.user.username} - Score: {self.total_score}/100"

class CodingProgress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coding_progress')
    platform_url = models.URLField(blank=True, null=True)
    solved_easy = models.IntegerField(default=0)
    solved_medium = models.IntegerField(default=0)
    solved_hard = models.IntegerField(default=0)
    total_contests = models.IntegerField(default=0)
    streak = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    @property
    def total_solved(self):
        return self.solved_easy + self.solved_medium + self.solved_hard

    def __str__(self):
        return f"{self.user.username} - {self.total_solved} solved"
