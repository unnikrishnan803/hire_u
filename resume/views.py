import os
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Resume, ResumeAnalysis

# Graceful optional import for PyMuPDF (fitz)
try:
    import pymupdf as fitz
except ImportError:
    try:
        import fitz
    except ImportError:
        fitz = None

@login_required
def upload_resume(request):
    if request.method == 'POST' and request.FILES.get('resume_file'):
        file = request.FILES['resume_file']
        resume = Resume.objects.create(user=request.user, file=file)
        
        # Extract Text using PyMuPDF if available, or fallback
        text = ""
        if fitz is not None:
            try:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                for page in doc:
                    text += page.get_text()
                doc.close()
            except Exception:
                pass
        else:
            try:
                raw_bytes = file.read()
                text = raw_bytes.decode('utf-8', errors='ignore')
            except Exception:
                pass

        resume.extracted_text = text
        resume.save()

        # Mock LLM / Rule-based Analysis Logic
        ats_score = random.randint(68, 88)
        analysis = ResumeAnalysis.objects.create(
            resume=resume,
            ats_score=ats_score,
            missing_keywords="Docker, AWS, REST API, Microservices",
            skill_gaps="System Design, Cloud Deployment, CI/CD",
            suggestions="Add measurable project results (e.g., 'Increased efficiency by 20%'). Improve technical skills section formatting."
        )
        return redirect('resume_analysis', analysis_id=analysis.id)
            
    return render(request, 'resume/upload.html')

@login_required
def resume_analysis(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, resume__user=request.user)
    context = {
        'analysis': analysis,
        'resume': analysis.resume
    }
    return render(request, 'resume/analysis.html', context)
