from django.db import models
from companies.models import Company

class Opportunity(models.Model):
    TYPE_CHOICES = (
        ('CAMPUS', 'Campus Placement'),
        ('INTERNSHIP', 'Internship'),
        ('OFF_CAMPUS', 'Off-campus Job'),
        ('HACKATHON', 'Hackathon'),
    )
    
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=255, blank=True, null=True)
    deadline = models.DateTimeField()
    
    # Eligibility rules
    cgpa_cutoff = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)
    allowed_backlogs = models.IntegerField(default=0)
    required_skills = models.TextField(blank=True, null=True, help_text="Comma separated skills")
    
    is_verified = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"

# Alias for blueprint alignment
RecruitmentDrive = Opportunity
