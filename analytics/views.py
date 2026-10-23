from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User, StudentProfile, Department
from assessment.models import AssessmentAttempt
from opportunities.models import Opportunity

@login_required
def officer_dashboard(request):
    if getattr(request.user, 'role', '') != 'OFFICER':
        return redirect('dashboard')
        
    students = StudentProfile.objects.all()
    total_students = students.count()
    
    # Calculate average readiness
    total_readiness = sum(s.overall_readiness for s in students)
    avg_readiness = int(total_readiness / total_students) if total_students > 0 else 0
    
    # At-risk students (readiness < 40)
    at_risk = students.filter(overall_readiness__lt=40).count()
    
    # Open Drives
    open_drives = Opportunity.objects.filter(status='OPEN').count()
    
    # Recent assessments
    recent_assessments = AssessmentAttempt.objects.order_by('-completed_at')[:5]
    
    context = {
        'total_students': total_students,
        'avg_readiness': avg_readiness,
        'at_risk': at_risk,
        'open_drives': open_drives,
        'students': students[:10], # Top 10 for preview
        'recent_assessments': recent_assessments,
    }
    return render(request, 'officer/dashboard.html', context)
