from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Skill, SkillProfile
from accounts.models import StudentProfile
from assessment.models import AssessmentAttempt
from hireu.services import calculate_readiness

@login_required
def skill_passport(request):
    if not hasattr(request.user, 'student_profile'):
        if request.user.role == 'OFFICER':
            return redirect('officer_dashboard')
        StudentProfile.objects.create(user=request.user)

    profile = request.user.student_profile

    # Core skill categories required by blueprint
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

    skills = SkillProfile.objects.filter(student=profile).select_related('skill').order_by('-mastery_percentage')

    # Rule-Based Skill-Gap Analysis
    # Benchmark targets based on career goal / target engineering roles
    target_role = profile.career_goal or "Software Developer"
    high_priority_gaps = []
    moderate_gaps = []
    mastered_skills = []

    for sp in skills:
        if sp.mastery_percentage < 45:
            high_priority_gaps.append({
                'name': sp.skill.name,
                'mastery': sp.mastery_percentage,
                'level': sp.level,
                'action': f"Focus on {sp.skill.name} fundamentals and beginner quizzes"
            })
        elif sp.mastery_percentage < 75:
            moderate_gaps.append({
                'name': sp.skill.name,
                'mastery': sp.mastery_percentage,
                'level': sp.level,
                'action': f"Advance {sp.skill.name} with timed tests and scenario problem-solving"
            })
        else:
            mastered_skills.append({
                'name': sp.skill.name,
                'mastery': sp.mastery_percentage,
                'level': sp.level
            })

    context = {
        'profile': profile,
        'skills': skills,
        'target_role': target_role,
        'high_priority_gaps': high_priority_gaps,
        'moderate_gaps': moderate_gaps,
        'mastered_skills': mastered_skills,
    }
    return render(request, 'career/skill_passport.html', context)


@login_required
def career_roadmap(request):
    if not hasattr(request.user, 'student_profile'):
        if request.user.role == 'OFFICER':
            return redirect('officer_dashboard')
        StudentProfile.objects.create(user=request.user)

    profile = request.user.student_profile
    skills_map = {sp.skill.name: sp.mastery_percentage for sp in SkillProfile.objects.filter(student=profile)}

    apt_score = skills_map.get('Aptitude', 0)
    tech_score = max(skills_map.get('Technical', 0), skills_map.get('Programming / DSA', 0))
    comm_score = skills_map.get('Communication', 0)
    iv_score = skills_map.get('Interview', 0)

    # 4-Phase Personalized Roadmap based on verified student performance
    phases = [
        {
            'number': 1,
            'title': 'Foundations & Aptitude Mastery',
            'desc': 'Build speed, accuracy, and quantitative problem-solving habits for campus screening tests.',
            'status': 'COMPLETED' if apt_score >= 70 else ('IN_PROGRESS' if apt_score > 0 else 'PENDING'),
            'score': apt_score,
            'milestones': [
                {'title': 'Quantitative Aptitude (Percentages, Profit & Loss, Speed-Distance)', 'done': apt_score >= 50},
                {'title': 'Logical Reasoning & Data Interpretation', 'done': apt_score >= 65},
                {'title': 'Verbal Ability & Reading Comprehension', 'done': apt_score >= 75},
            ]
        },
        {
            'number': 2,
            'title': 'Core Technicals & Data Structures (DSA)',
            'desc': 'Deep dive into algorithmic problems, database queries, and object-oriented architecture.',
            'status': 'COMPLETED' if tech_score >= 75 else ('IN_PROGRESS' if tech_score > 0 else 'PENDING'),
            'score': tech_score,
            'milestones': [
                {'title': 'Arrays, Strings, Stacks, Queues & HashMaps', 'done': tech_score >= 45},
                {'title': 'Trees, Graphs, Recursion & Dynamic Programming', 'done': tech_score >= 70},
                {'title': 'DBMS, SQL Queries & Normalization', 'done': tech_score >= 80},
            ]
        },
        {
            'number': 3,
            'title': 'Communication & Domain Projects',
            'desc': 'Develop articulate presentation skills, project explanations, and situational HR responses.',
            'status': 'COMPLETED' if comm_score >= 75 else ('IN_PROGRESS' if comm_score > 0 else 'PENDING'),
            'score': comm_score,
            'milestones': [
                {'title': 'Professional Elevator Pitch & Self Introduction', 'done': comm_score >= 45},
                {'title': 'STAR Method for Behavioral & Situational Questions', 'done': comm_score >= 65},
                {'title': 'Project Architecture & Technical Deep-Dive Explanation', 'done': comm_score >= 75},
            ]
        },
        {
            'number': 4,
            'title': 'Mock Interviews & Company Drive Readiness',
            'desc': 'Full-length simulated placement drives, rubric feedback, and target company applications.',
            'status': 'COMPLETED' if (iv_score >= 75 and profile.overall_readiness >= 80) else ('IN_PROGRESS' if iv_score > 0 else 'PENDING'),
            'score': iv_score,
            'milestones': [
                {'title': 'Verified ATS-Ready Resume with Key Impact Metrics', 'done': profile.overall_readiness >= 50},
                {'title': 'AI Mock Interview with Technical & Behavioral Feedback', 'done': iv_score >= 60},
                {'title': 'Eligible & Target-Ready for 5 Campus Recruitment Drives', 'done': profile.overall_readiness >= 75},
            ]
        },
    ]

    context = {
        'profile': profile,
        'phases': phases,
        'target_goal': profile.career_goal or "Software Engineer",
    }
    return render(request, 'career/roadmap.html', context)
