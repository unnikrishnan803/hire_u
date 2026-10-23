from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class TargetRole(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='roles')
    role_name = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.role_name} at {self.company.name}"
