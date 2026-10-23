from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import Assessment, AssessmentAttempt, Question, Answer
from hireu.services import process_assessment_results, award_xp, create_notification, calculate_readiness

@login_required
def assessment_list(request):
    assessments = Assessment.objects.filter(is_active=True)
    attempts = AssessmentAttempt.objects.filter(user=request.user).order_by('-completed_at', '-id')
    completed_ids = set(attempts.values_list('assessment_id', flat=True))
    
    # Annotate attempts with percentage and level for display
    attempt_list = []
    for att in attempts:
        pct = int(round((att.score / att.max_score) * 100)) if att.max_score > 0 else 0
        if pct >= 75:
            lvl = 'Advanced'
            lvl_class = 'pill-green'
        elif pct >= 45:
            lvl = 'Normal'
            lvl_class = 'pill-yellow'
        else:
            lvl = 'Beginner'
            lvl_class = 'pill-orange'
        attempt_list.append({
            'attempt': att,
            'percentage': pct,
            'level': lvl,
            'level_class': lvl_class,
        })

    context = {
        'assessments': assessments,
        'completed_ids': completed_ids,
        'attempts': attempt_list,
    }
    return render(request, 'assessment/list.html', context)

@login_required
def take_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id, is_active=True)

    if request.method == 'POST':
        # Retrieve the exact question IDs submitted by the client
        submitted_q_ids = request.POST.getlist('question_ids')
        if submitted_q_ids:
            # Preserve order or filter by submitted questions
            id_list = [int(qid) for qid in submitted_q_ids if str(qid).isdigit()]
            questions_qs = Question.objects.filter(id__in=id_list, section__assessment=assessment)
            # Create a lookup map for exact grading
            q_map = {q.id: q for q in questions_qs}
            questions = [q_map[qid] for qid in id_list if qid in q_map]
        else:
            questions = list(Question.objects.filter(section__assessment=assessment))

        total_questions = len(questions)
        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            assessment=assessment,
            max_score=total_questions
        )

        score = 0
        for q in questions:
            selected = request.POST.get(f'question_{q.id}')
            is_correct = bool(selected and selected.strip().upper() == q.correct_option.strip().upper())
            if is_correct:
                score += 1
            Answer.objects.create(
                attempt=attempt,
                question=q,
                selected_option=selected,
                is_correct=is_correct
            )

        attempt.score = score
        attempt.completed_at = timezone.now()
        attempt.save()

        # Update SkillProfiles in career app
        process_assessment_results(attempt)

        # Update student profile overall readiness
        if hasattr(request.user, 'student_profile'):
            profile = request.user.student_profile
            rd = calculate_readiness(profile)
            profile.overall_readiness = rd['overall']
            profile.save()

            # Award XP and check badges
            award_xp(profile, xp_amount=100, reason=f"{assessment.title} completed")

        # Notify user
        pct = int(round((score / total_questions) * 100)) if total_questions > 0 else 0
        create_notification(
            request.user,
            f'{assessment.title} Completed',
            f'You scored {score}/{total_questions} ({pct}%). Your Skill Passport has been updated.',
            'SUCCESS'
        )

        return redirect('assessment_result', attempt_id=attempt.id)

    # GET request: load questions for this assessment
    questions = list(Question.objects.filter(section__assessment=assessment).order_by('id')[:20])
    context = {
        'assessment': assessment,
        'questions': questions,
        'total': len(questions),
    }
    return render(request, 'assessment/take.html', context)

@login_required
def assessment_result(request, attempt_id):
    # Enforce access control: user can only view their own attempts
    attempt = get_object_or_404(AssessmentAttempt, id=attempt_id, user=request.user)
    percentage = int(round((attempt.score / attempt.max_score) * 100)) if attempt.max_score > 0 else 0

    if percentage >= 75:
        level = "Advanced"
        level_class = "pill-green"
    elif percentage >= 45:
        level = "Normal"
        level_class = "pill-yellow"
    else:
        level = "Beginner"
        level_class = "pill-orange"

    answers = Answer.objects.filter(attempt=attempt).select_related('question')
    all_attempts = AssessmentAttempt.objects.filter(user=request.user).order_by('-completed_at')[:5]

    context = {
        'attempt': attempt,
        'percentage': percentage,
        'level': level,
        'level_class': level_class,
        'answers': answers,
        'all_attempts': all_attempts,
    }
    return render(request, 'assessment/result.html', context)

@login_required
def complete_task(request, task_id):
    """AJAX endpoint to mark a daily task as completed."""
    if request.method == 'POST':
        from learning.models import DailyTask
        if not hasattr(request.user, 'student_profile'):
            return JsonResponse({'status': 'error', 'message': 'Profile required'}, status=400)
        task = get_object_or_404(DailyTask, id=task_id, student=request.user.student_profile)
        task.status = 'COMPLETED'
        task.save()
        award_xp(request.user.student_profile, task.xp_reward)
        return JsonResponse({'status': 'ok', 'xp': task.xp_reward})
    return JsonResponse({'status': 'error'}, status=400)
