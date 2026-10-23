from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import InterviewSession, InterviewQuestion, InterviewAnswer, CodingProgress
from hireu.services import award_xp, create_notification
import random

INTERVIEW_RUBRIC = {
    'technical_weight': 40,
    'relevance_weight': 20,
    'explanation_weight': 20,
    'communication_weight': 10,
    'completeness_weight': 10,
}

@login_required
def mock_interview(request):
    sessions = InterviewSession.objects.filter(user=request.user).order_by('-created_at')
    modes = [('HR','HR Interview'), ('TECHNICAL','Technical Interview'), ('COMPANY','Company Interview')]
    context = {'sessions': sessions, 'modes': modes}
    return render(request, 'interview/mock_interview.html', context)

@login_required
def start_interview(request, mode):
    if request.method != 'POST':
        return redirect('mock_interview')

    session = InterviewSession.objects.create(user=request.user, mode=mode.upper())
    questions = list(InterviewQuestion.objects.filter(mode=mode.upper()).order_by('?')[:5])

    if not questions:
        # Seed some default questions if none exist
        seed_interview_questions()
        questions = list(InterviewQuestion.objects.filter(mode=mode.upper()).order_by('?')[:5])

    request.session[f'interview_{session.id}_questions'] = [q.id for q in questions]
    request.session[f'interview_{session.id}_current']   = 0

    return redirect('interview_question', session_id=session.id)

@login_required
def interview_question(request, session_id):
    session   = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    q_ids     = request.session.get(f'interview_{session.id}_questions', [])
    current   = request.session.get(f'interview_{session.id}_current', 0)

    if current >= len(q_ids):
        return redirect('interview_result', session_id=session.id)

    question  = get_object_or_404(InterviewQuestion, id=q_ids[current])
    total     = len(q_ids)

    if request.method == 'POST':
        answer_text = request.POST.get('answer','').strip()

        # Mock evaluation — in production, call LLM here
        # Rubric scores based on answer length as proxy
        word_count = len(answer_text.split())
        base = min(int(word_count * 1.5), 100)
        tech    = min(int(base * 0.40), 40)
        relev   = min(int(base * 0.20), 20)
        explan  = min(int(base * 0.18), 20)
        comm    = min(int(base * 0.10), 10)
        comp    = min(int(base * 0.08), 10)

        InterviewAnswer.objects.create(
            session=session, question=question,
            student_answer=answer_text,
            score_technical=tech, score_relevance=relev,
            score_explanation=explan, score_communication=comm,
            score_completeness=comp,
            feedback=f"Good attempt. Aim to include concrete examples. Technical points: {tech}/40."
        )

        request.session[f'interview_{session.id}_current'] = current + 1
        return redirect('interview_question', session_id=session.id)

    context = {
        'session':  session,
        'question': question,
        'current':  current + 1,
        'total':    total,
        'progress': int(((current) / total) * 100),
    }
    return render(request, 'interview/question.html', context)

@login_required
def interview_result(request, session_id):
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
    answers = session.answers.select_related('question').all()

    total_score = sum(a.total_score for a in answers)
    max_possible = len(answers) * 100
    pct = int((total_score / max_possible) * 100) if max_possible else 0

    session.overall_score = pct
    session.status = 'COMPLETED'
    session.strengths = "Concept understanding, Willingness to explain"
    session.weaknesses = "Add more concrete examples, Improve completeness"
    session.recommendations = "Practice STAR method for HR questions, Study OOP examples for technical."
    session.save()

    award_xp(request.user.student_profile, 50, "Mock Interview Completed")
    create_notification(request.user, 'Interview Complete', f'You scored {pct}% in your mock interview.', 'SUCCESS')

    context = {'session': session, 'answers': answers, 'pct': pct}
    return render(request, 'interview/result.html', context)

@login_required
def coding_progress(request):
    prog, created = CodingProgress.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        prog.solved_easy   = int(request.POST.get('easy', 0))
        prog.solved_medium = int(request.POST.get('medium', 0))
        prog.solved_hard   = int(request.POST.get('hard', 0))
        prog.total_contests = int(request.POST.get('contests', 0))
        prog.platform_url  = request.POST.get('platform_url','')
        prog.save()

    context = {'prog': prog}
    return render(request, 'interview/coding_progress.html', context)

def seed_interview_questions():
    """Seeds default interview questions if none exist."""
    defaults = [
        ('HR', "Tell me about yourself.", "Introduce background, skills, career goals."),
        ('HR', "What are your strengths and weaknesses?", "Self-awareness, honesty, growth mindset."),
        ('HR', "Where do you see yourself in 5 years?", "Aligned with company growth, role ambition."),
        ('TECHNICAL', "Explain polymorphism in OOP.", "Compile-time (overloading) vs runtime (overriding) polymorphism."),
        ('TECHNICAL', "What is the time complexity of Merge Sort?", "O(n log n) — divide and conquer."),
        ('TECHNICAL', "Explain the difference between SQL JOIN types.", "INNER, LEFT, RIGHT, FULL OUTER JOINs with examples."),
        ('COMPANY', "Why do you want to work at our company?", "Research about company, alignment with values."),
        ('COMPANY', "Describe a challenging project you worked on.", "STAR method: Situation, Task, Action, Result."),
    ]
    for mode, qtext, ideal in defaults:
        InterviewQuestion.objects.get_or_create(mode=mode, question_text=qtext, defaults={'ideal_answer_points': ideal})
