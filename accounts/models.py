from django.db import models
from django.contrib.auth.models import AbstractUser
from companies.models import Company

class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('OFFICER', 'Placement Officer'),
        ('COMPANY', 'Company/Recruiter'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STUDENT')
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    
    def __str__(self):
        return self.name

class CareerTrack(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='career_tracks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.department.code})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    year = models.IntegerField(blank=True, null=True)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    backlogs = models.IntegerField(default=0)
    career_goal = models.CharField(max_length=255, blank=True, null=True)
    career_track = models.ForeignKey(CareerTrack, on_delete=models.SET_NULL, null=True, blank=True)
    target_companies = models.ManyToManyField(Company, blank=True)
    
    overall_readiness = models.IntegerField(default=0)
    onboarding_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} Profile"
