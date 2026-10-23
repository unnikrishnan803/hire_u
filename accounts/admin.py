from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department, CareerTrack, StudentProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('HireU Fields', {'fields': ('role', 'phone')}),
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')

@admin.register(CareerTrack)
class CareerTrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department',)

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'year', 'cgpa', 'overall_readiness', 'onboarding_completed')
    list_filter = ('department', 'year', 'onboarding_completed')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'career_goal')
