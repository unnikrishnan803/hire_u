from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User, StudentProfile, Department, CareerTrack
from companies.models import Company

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip().lower()
        password   = request.POST.get('password', '')

        # Validation
        if not first_name or not last_name:
            messages.error(request, "First and last name are required.")
            return render(request, 'accounts/register.html')

        if not email:
            messages.error(request, "A valid email is required.")
            return render(request, 'accounts/register.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Please enter a valid email address.")
            return render(request, 'accounts/register.html')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'accounts/register.html')

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name, role='STUDENT'
        )
        StudentProfile.objects.create(user=user)
        login(request, user)
        messages.success(request, f"Welcome to HireU, {first_name}! Let's set up your profile.")
        return redirect('onboarding')
    return render(request, 'accounts/register.html')


def login_view(request):
    if request.user.is_authenticated:
        if getattr(request.user, 'role', '') == 'OFFICER':
            return redirect('officer_dashboard')
        return redirect('dashboard')
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'OFFICER':
                return redirect('officer_dashboard')
            profile = getattr(user, 'student_profile', None)
            if profile and not profile.onboarding_completed:
                return redirect('onboarding')
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('landing')


@login_required
def onboarding_view(request):
    if getattr(request.user, 'role', '') != 'STUDENT':
        return redirect('dashboard')
    try:
        profile = request.user.student_profile
    except Exception:
        profile = StudentProfile.objects.create(user=request.user)

    if profile.onboarding_completed:
        return redirect('dashboard')

    if request.method == 'POST':
        dept_id      = request.POST.get('department')
        year         = request.POST.get('year')
        cgpa         = request.POST.get('cgpa')
        backlogs     = request.POST.get('backlogs', 0)
        career_goal  = request.POST.get('career_goal', '').strip()
        track_id     = request.POST.get('career_track')
        
        # Deduplicate and limit to 5 companies
        raw_company_ids = request.POST.getlist('companies')
        company_ids = list(dict.fromkeys([cid for cid in raw_company_ids if cid.isdigit()]))[:5]

        if dept_id:      profile.department_id  = dept_id
        if year:         profile.year            = int(year)
        if cgpa:         profile.cgpa            = float(cgpa)
        if backlogs is not None and str(backlogs).isdigit():
            profile.backlogs = int(backlogs)
        if career_goal:  profile.career_goal     = career_goal
        if track_id:     profile.career_track_id = track_id
        profile.onboarding_completed = True
        profile.save()

        if company_ids:
            profile.target_companies.set(company_ids)

        # Create gamification record
        from gamification.models import Gamification
        Gamification.objects.get_or_create(student=profile)

        # Initialize core skill categories if not present
        from career.models import Skill, SkillProfile
        core_skills = [
            ('Aptitude', 'Aptitude'),
            ('Technical', 'Technical'),
            ('Programming / DSA', 'Technical'),
            ('Communication', 'Soft Skill'),
            ('Interview', 'Soft Skill'),
            ('Resume', 'Career Prep'),
        ]
        for sk_name, sk_cat in core_skills:
            sk_obj, _ = Skill.objects.get_or_create(name=sk_name, defaults={'category': sk_cat})
            SkillProfile.objects.get_or_create(student=profile, skill=sk_obj, defaults={'level': 'BEGINNER', 'mastery_percentage': 0})

        from hireu.services import create_notification
        create_notification(request.user, 'Profile Complete!',
            'Welcome to HireU! Take your initial assessment to get started.', 'SUCCESS')

        messages.success(request, "Profile set up! Now take your initial assessments.")
        return redirect('assessments')

    context = {
        'departments': Department.objects.all(),
        'tracks':      CareerTrack.objects.all(),
        'companies':   Company.objects.all(),
    }
    return render(request, 'accounts/onboarding.html', context)


@login_required
def profile_view(request):
    """View student profile."""
    if not hasattr(request.user, 'student_profile'):
        if request.user.role == 'OFFICER':
            return redirect('officer_dashboard')
        StudentProfile.objects.create(user=request.user)

    profile = request.user.student_profile
    context = {
        'profile': profile,
        'user': request.user,
        'target_companies': profile.target_companies.all(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Edit student profile."""
    if not hasattr(request.user, 'student_profile'):
        if request.user.role == 'OFFICER':
            return redirect('officer_dashboard')
        StudentProfile.objects.create(user=request.user)

    profile = request.user.student_profile
    user = request.user

    if request.method == 'POST':
        first_name   = request.POST.get('first_name', '').strip()
        last_name    = request.POST.get('last_name', '').strip()
        phone        = request.POST.get('phone', '').strip()
        dept_id      = request.POST.get('department')
        year         = request.POST.get('year')
        cgpa         = request.POST.get('cgpa')
        backlogs     = request.POST.get('backlogs')
        career_goal  = request.POST.get('career_goal', '').strip()
        track_id     = request.POST.get('career_track')
        
        # Deduplicate and limit to 5 companies
        raw_company_ids = request.POST.getlist('companies')
        company_ids = list(dict.fromkeys([cid for cid in raw_company_ids if cid.isdigit()]))[:5]

        # Update User fields
        if first_name: user.first_name = first_name
        if last_name:  user.last_name = last_name
        user.phone = phone
        user.save()

        # Update Profile fields
        if dept_id:
            profile.department_id = dept_id
        elif dept_id == '':
            profile.department = None

        if year:
            profile.year = int(year)
        if cgpa:
            try:
                profile.cgpa = float(cgpa)
            except ValueError:
                pass
        if backlogs is not None and str(backlogs).isdigit():
            profile.backlogs = int(backlogs)

        profile.career_goal = career_goal

        if track_id:
            profile.career_track_id = track_id
        elif track_id == '':
            profile.career_track = None

        profile.save()
        profile.target_companies.set(company_ids)

        # Recalculate readiness
        from hireu.services import calculate_readiness
        rd = calculate_readiness(profile)
        profile.overall_readiness = rd['overall']
        profile.save()

        messages.success(request, "Your profile has been updated successfully!")
        return redirect('profile')

    context = {
        'profile': profile,
        'departments': Department.objects.all(),
        'tracks': CareerTrack.objects.all(),
        'companies': Company.objects.all(),
        'selected_company_ids': set(profile.target_companies.values_list('id', flat=True)),
    }
    return render(request, 'accounts/profile_edit.html', context)
