"""
HireU Services Layer.
Contains the core business logic for adaptive training, readiness calculation,
eligibility checking, and gamification.
"""

from django.utils import timezone
from django.db import transaction
import datetime


# ─────────────────────────────────────────────
# READINESS SERVICE
# Weights per project spec (Section 25 of blueprint)
# ─────────────────────────────────────────────
READINESS_WEIGHTS = {
    'aptitude': 0.15,
    'technical': 0.20,
    'dsa': 0.15,
    'communication': 0.10,
    'interview': 0.15,
    'resume': 0.10,
    'consistency': 0.15,
}

def calculate_readiness(student_profile):
    """
    Calculates the weighted overall readiness score for a student.
    This is deterministic (rule-based), not ML.
    """
    from career.models import SkillProfile
    from learning.models import DailyTask
    from resume.models import Resume

    sp = student_profile
    skill_map = {}
    for s in SkillProfile.objects.filter(student=sp):
        skill_map[s.skill.name.lower()] = s.mastery_percentage

    aptitude = skill_map.get('aptitude', 0)
    technical = skill_map.get('technical', 0)
    dsa = skill_map.get('programming / dsa', skill_map.get('dsa', 0))
    communication = skill_map.get('communication', 0)
    interview = skill_map.get('interview', 0)

    # Resume score: 100 if uploaded, else 0
    has_resume = Resume.objects.filter(user=sp.user).exists()
    resume_score = skill_map.get('resume', 100 if has_resume else 0)

    # Consistency: task completion rate over last 7 days
    today = timezone.now().date()
    week_ago = today - datetime.timedelta(days=7)
    tasks_last_week = DailyTask.objects.filter(student=sp, date__gte=week_ago)
    total_tasks = tasks_last_week.count()
    completed_tasks = tasks_last_week.filter(status='COMPLETED').count()
    consistency = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    readiness = (
        aptitude * READINESS_WEIGHTS['aptitude'] +
        technical * READINESS_WEIGHTS['technical'] +
        dsa * READINESS_WEIGHTS['dsa'] +
        communication * READINESS_WEIGHTS['communication'] +
        interview * READINESS_WEIGHTS['interview'] +
        resume_score * READINESS_WEIGHTS['resume'] +
        consistency * READINESS_WEIGHTS['consistency']
    )

    return {
        'overall': int(readiness),
        'aptitude': aptitude,
        'technical': technical,
        'dsa': dsa,
        'communication': communication,
        'interview': interview,
        'resume': resume_score,
        'consistency': consistency,
    }


# ─────────────────────────────────────────────
# ELIGIBILITY SERVICE
# Drive-specific checks, NOT permanent company rules
# ─────────────────────────────────────────────
def check_eligibility(student_profile, drive):
    """
    Returns eligibility status for a student against a specific recruitment drive.
    Returns: dict with status ('ELIGIBLE', 'NEAR_TARGET', 'NOT_ELIGIBLE') and checks list.
    """
    sp = student_profile
    checks = []
    all_pass = True
    has_warning = False

    # CGPA check
    if sp.cgpa is not None and sp.cgpa >= drive.cgpa_cutoff:
        checks.append({'label': 'CGPA', 'passed': True, 'detail': f'{sp.cgpa} ≥ {drive.cgpa_cutoff}'})
    else:
        checks.append({'label': 'CGPA', 'passed': False, 'detail': f'{sp.cgpa or "N/A"} < {drive.cgpa_cutoff}'})
        all_pass = False

    # Backlog check
    if sp.backlogs <= drive.allowed_backlogs:
        checks.append({'label': 'Backlogs', 'passed': True, 'detail': f'{sp.backlogs} active backlog(s)'})
    else:
        checks.append({'label': 'Backlogs', 'passed': False, 'detail': f'Has {sp.backlogs} backlog(s), max allowed: {drive.allowed_backlogs}'})
        all_pass = False

    # Branch check (if drive specifies branches)
    if drive.required_skills:
        from career.models import SkillProfile
        required = [s.strip() for s in drive.required_skills.split(',')]
        for req_skill in required:
            sp_skill = SkillProfile.objects.filter(
                student=sp, skill__name__iexact=req_skill
            ).first()
            if sp_skill and sp_skill.mastery_percentage >= 40:
                checks.append({'label': req_skill, 'passed': True, 'detail': f'{sp_skill.mastery_percentage}% mastery'})
            else:
                mastery = sp_skill.mastery_percentage if sp_skill else 0
                checks.append({'label': req_skill, 'passed': False, 'detail': f'Only {mastery}% mastery'})
                has_warning = True

    if all_pass and not has_warning:
        status = 'ELIGIBLE'
    elif all_pass and has_warning:
        status = 'NEAR_TARGET'
    else:
        status = 'NOT_ELIGIBLE'

    return {'status': status, 'checks': checks}


# ─────────────────────────────────────────────
# SKILL LEVEL SERVICE
# Maps percentage → Beginner / Normal / Advanced
# ─────────────────────────────────────────────
def get_skill_level(mastery_pct):
    if mastery_pct >= 75:
        return 'ADVANCED'
    elif mastery_pct >= 45:
        return 'NORMAL'
    else:
        return 'BEGINNER'


# ─────────────────────────────────────────────
# ASSESSMENT SCORING SERVICE
# Calculates score and updates SkillProfile
# ─────────────────────────────────────────────
def process_assessment_results(attempt):
    """
    After an attempt is saved, update the student's SkillProfiles.
    """
    from career.models import Skill, SkillProfile

    if not attempt.max_score:
        return

    pct = int(round((attempt.score / attempt.max_score) * 100))
    atype = attempt.assessment.type

    # Map assessment type to target skill names
    type_skill_map = {
        'APTITUDE': ['Aptitude'],
        'TECHNICAL': ['Technical', 'Programming / DSA'],
        'COMMUNICATION': ['Communication'],
    }

    skill_names = type_skill_map.get(atype, [])
    if not skill_names:
        return

    sp = attempt.user.student_profile
    for skill_name in skill_names:
        skill, _ = Skill.objects.get_or_create(name=skill_name)
        skill_profile, created = SkillProfile.objects.get_or_create(
            student=sp,
            skill=skill,
            defaults={'mastery_percentage': pct, 'level': get_skill_level(pct)}
        )

        if not created:
            old = skill_profile.mastery_percentage
            # Weighted average: 60% recent, 40% history
            new_mastery = int(round(pct * 0.6 + old * 0.4))
            skill_profile.mastery_percentage = new_mastery
            skill_profile.level = get_skill_level(new_mastery)
            skill_profile.trend = 'Improving' if new_mastery > old else ('Declining' if new_mastery < old else 'Stable')
            skill_profile.save()

    # Regenerate daily tasks based on updated skill profile
    generate_daily_tasks(sp, force_regenerate=True)


# ─────────────────────────────────────────────
# ADAPTIVE TRAINING SERVICE
# Generates daily task priorities based on student data
# ─────────────────────────────────────────────
TASK_TEMPLATES = {
    'DSA': [
        {'title': 'Arrays & Strings Practice', 'difficulty': 'EASY', 'minutes': 15, 'xp': 30},
        {'title': 'Linked Lists & Trees', 'difficulty': 'MEDIUM', 'minutes': 25, 'xp': 50},
        {'title': 'Dynamic Programming Problems', 'difficulty': 'HARD', 'minutes': 40, 'xp': 100},
    ],
    'SQL': [
        {'title': 'SQL SELECT & Filtering', 'difficulty': 'EASY', 'minutes': 10, 'xp': 20},
        {'title': 'SQL Joins Practice', 'difficulty': 'MEDIUM', 'minutes': 20, 'xp': 40},
        {'title': 'Subqueries & Aggregations', 'difficulty': 'HARD', 'minutes': 30, 'xp': 70},
    ],
    'Aptitude': [
        {'title': '10 Quantitative Aptitude Questions', 'difficulty': 'EASY', 'minutes': 15, 'xp': 30},
        {'title': 'Logical Reasoning Practice Set', 'difficulty': 'MEDIUM', 'minutes': 20, 'xp': 40},
        {'title': 'Data Interpretation Timed Test', 'difficulty': 'HARD', 'minutes': 25, 'xp': 60},
    ],
    'Communication': [
        {'title': 'Grammar & Vocabulary Drill', 'difficulty': 'EASY', 'minutes': 10, 'xp': 20},
        {'title': 'Self Introduction Practice', 'difficulty': 'MEDIUM', 'minutes': 15, 'xp': 30},
        {'title': 'Situational HR Mock Q&A', 'difficulty': 'MEDIUM', 'minutes': 20, 'xp': 50},
    ],
    'Technical': [
        {'title': 'OOP Concepts Revision', 'difficulty': 'EASY', 'minutes': 15, 'xp': 30},
        {'title': 'DBMS & Normalization', 'difficulty': 'MEDIUM', 'minutes': 20, 'xp': 40},
        {'title': 'System Design Intro', 'difficulty': 'HARD', 'minutes': 35, 'xp': 80},
    ],
}

def calculate_priority_score(mastery_pct, company_requirement=False, recent_failure=False):
    """Determines priority based on gap, company need, and recent failures."""
    gap_score = max(0, 70 - mastery_pct) * 0.6
    company_bonus = 20 if company_requirement else 0
    failure_bonus = 15 if recent_failure else 0
    return gap_score + company_bonus + failure_bonus

def generate_daily_tasks(student_profile, force_regenerate=False):
    """
    Generates today's adaptive tasks for a student.
    Based on: skill gaps, weak areas, career track, target companies.
    """
    from career.models import SkillProfile
    from learning.models import DailyTask

    today = timezone.now().date()

    # Don't regenerate if tasks exist for today
    if DailyTask.objects.filter(student=student_profile, date=today).exists() and not force_regenerate:
        return DailyTask.objects.filter(student=student_profile, date=today)

    # Remove old tasks for today if force_regenerate
    if force_regenerate:
        DailyTask.objects.filter(student=student_profile, date=today).delete()

    # Get skill profiles
    skills = {sp.skill.name: sp.mastery_percentage for sp in SkillProfile.objects.filter(student=student_profile)}

    # Calculate priority for each skill area
    priorities = {}
    for area in TASK_TEMPLATES.keys():
        mastery = skills.get(area, 0)
        priorities[area] = calculate_priority_score(mastery)

    # Sort by priority descending, take top 3-4 skill areas
    sorted_areas = sorted(priorities.items(), key=lambda x: x[1], reverse=True)
    top_areas = [area for area, _ in sorted_areas[:4]]

    tasks_created = []
    with transaction.atomic():
        for area in top_areas:
            mastery = skills.get(area, 0)
            level = get_skill_level(mastery)

            # Pick difficulty based on skill level
            if level == 'BEGINNER':
                template = TASK_TEMPLATES[area][0]
            elif level == 'NORMAL':
                template = TASK_TEMPLATES[area][1]
            else:
                template = TASK_TEMPLATES[area][2]

            task = DailyTask.objects.create(
                student=student_profile,
                title=template['title'],
                skill_area=area,
                difficulty=template['difficulty'],
                estimated_minutes=template['minutes'],
                xp_reward=template['xp'],
                date=today,
            )
            tasks_created.append(task)

    return tasks_created


# ─────────────────────────────────────────────
# GAMIFICATION SERVICE
# Awards XP and badges
# ─────────────────────────────────────────────
def award_xp(student_profile, xp_amount, reason="Task completed"):
    from gamification.models import Gamification
    from notifications.models import Notification

    gami, _ = Gamification.objects.get_or_create(student=student_profile)
    gami.xp += xp_amount

    # Update streak
    today = timezone.now().date()
    if gami.last_active_date:
        delta = (today - gami.last_active_date).days
        if delta == 1:
            gami.streak += 1
        elif delta > 1:
            gami.streak = 1
    else:
        gami.streak = 1

    gami.last_active_date = today
    gami.save()

    # Check and award streak badge
    check_and_award_badges(student_profile, gami)

    return gami

def check_and_award_badges(student_profile, gami):
    from gamification.models import Badge, StudentBadge

    badge_rules = [
        ('first-assessment', lambda sp, g: True),  # Always award on first call
        ('seven-day-streak', lambda sp, g: g.streak >= 7),
        ('veteran-streak', lambda sp, g: g.streak >= 30),
    ]

    for slug, condition in badge_rules:
        try:
            badge = Badge.objects.get(slug=slug)
            if condition(student_profile, gami) and not StudentBadge.objects.filter(student=student_profile, badge=badge).exists():
                StudentBadge.objects.create(student=student_profile, badge=badge)
        except Badge.DoesNotExist:
            pass


# ─────────────────────────────────────────────
# NOTIFICATION SERVICE
# ─────────────────────────────────────────────
def create_notification(user, title, message, ntype='INFO'):
    from notifications.models import Notification
    Notification.objects.create(user=user, title=title, message=message, type=ntype)
