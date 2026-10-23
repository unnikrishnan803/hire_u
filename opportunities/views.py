from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Opportunity
from django.utils import timezone

@login_required
def opportunity_hub(request):
    profile = request.user.student_profile
    opportunities = Opportunity.objects.filter(status='OPEN', deadline__gte=timezone.now()).order_by('deadline')
    
    # Calculate eligibility for each opportunity
    for opp in opportunities:
        eligible = True
        reasons = []
        
        if profile.cgpa < opp.cgpa_cutoff:
            eligible = False
            reasons.append(f"CGPA below {opp.cgpa_cutoff}")
            
        if profile.backlogs > opp.allowed_backlogs:
            eligible = False
            reasons.append(f"Backlogs exceed {opp.allowed_backlogs}")
            
        opp.is_eligible = eligible
        opp.ineligibility_reasons = reasons
    
    context = {
        'opportunities': opportunities
    }
    return render(request, 'opportunities/hub.html', context)
