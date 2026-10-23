from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import datetime
from accounts.models import StudentProfile
from assessment.models import Assessment, AssessmentAttempt
from career.models import SkillProfile
from learning.models import DailyTask
from hireu.services import generate_daily_tasks, calculate_readiness
from opportunities.models import Opportunity, RecruitmentDrive


@login_required
def dashboard_view(request):
    if getattr(request.user, 'role', '') == 'OFFICER':
        return redirect('officer_dashboard')

    profile = getattr(request.user, 'student_profile', None)
    if not profile:
        profile = StudentProfile.objects.create(user=request.user)

    if not profile.onboarding_completed:
        return redirect('onboarding')

    today   = timezone.now().date()
    hour    = timezone.localtime(timezone.now()).hour

    if   hour < 12: greeting = "Morning"
    elif hour < 17: greeting = "Afternoon"
    else:           greeting = "Evening"

    # Gamification
    gami = getattr(profile, 'gamification', None)

    # Generate tasks for today if none exist
    generate_daily_tasks(profile)
    tasks = DailyTask.objects.filter(student=profile, date=today)
    today_total     = tasks.count()
    today_completed = tasks.filter(status='COMPLETED').count()
    today_pct       = int((today_completed / today_total) * 100) if today_total else 0

    # Weak skills (mastery < 75%)
    weak_skills = SkillProfile.objects.filter(
        student=profile, mastery_percentage__lt=75
    ).order_by('mastery_percentage')[:5]

    # Assessments
    all_assessments = Assessment.objects.filter(is_active=True)
    completed_ids   = set(AssessmentAttempt.objects.filter(user=request.user).values_list('assessment_id', flat=True))

    # Target companies with real readiness derived from profile and drive requirements
    companies = []
    base_readiness = profile.overall_readiness
    for comp in profile.target_companies.all():
        # Check if company has an active recruitment drive
        drive = Opportunity.objects.filter(company=comp, status='OPEN').first()
        if drive:
            # Check eligibility and compute readiness relative to cutoff & skills
            cgpa_factor = 1.0
            if profile.cgpa and drive.cgpa_cutoff:
                cgpa_factor = min(float(profile.cgpa) / float(drive.cgpa_cutoff), 1.0)
            backlog_penalty = 15 if (profile.backlogs > drive.allowed_backlogs) else 0
            comp_readiness = max(0, min(100, int(base_readiness * cgpa_factor - backlog_penalty)))
        else:
            comp_readiness = base_readiness

        comp.readiness = comp_readiness
        companies.append(comp)

    context = {
        'profile':         profile,
        'gami':            gami,
        'greeting':        greeting,
        'today_date':      today.strftime('%d %b %Y'),
        'tasks':           tasks,
        'today_total':     today_total,
        'today_completed': today_completed,
        'today_pct':       today_pct,
        'weak_skills':     weak_skills,
        'all_assessments': all_assessments,
        'completed_ids':   completed_ids,
        'companies':       companies,
    }
    return render(request, 'student/dashboard.html', context)


def landing_page(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'role', '') == 'OFFICER':
            return redirect('officer_dashboard')
        return redirect('dashboard')
    return render(request, 'landing.html')
