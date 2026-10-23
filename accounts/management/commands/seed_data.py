from django.core.management.base import BaseCommand
from accounts.models import Department, CareerTrack, User, StudentProfile
from companies.models import Company
from career.models import Skill, SkillProfile
from assessment.models import Assessment, AssessmentSection, Question, AssessmentAttempt, Answer
from gamification.models import Gamification, Badge, StudentBadge
from notifications.models import Notification
from opportunities.models import Opportunity
from interview.models import InterviewQuestion
from django.utils import timezone
import datetime
import random

class Command(BaseCommand):
    help = 'Seeds the entire HireU database with realistic demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('🚀 Seeding HireU...'))

        # ── Departments ──────────────────────────────────────
        depts_data = [
            ('Computer Science Engineering', 'CSE'),
            ('Information Technology', 'IT'),
            ('Electronics & Communication Engineering', 'ECE'),
            ('Electrical & Electronics Engineering', 'EEE'),
            ('Mechanical Engineering', 'MECH'),
            ('Civil Engineering', 'CIVIL'),
        ]
        depts = {}
        for name, code in depts_data:
            d, _ = Department.objects.get_or_create(code=code, defaults={'name': name})
            depts[code] = d
        self.stdout.write('  ✓ Departments')

        # ── Career Tracks ─────────────────────────────────────
        tracks_data = [
            ('CSE',  'Software Developer (SDE)'),
            ('CSE',  'Data Science / ML'),
            ('IT',   'Software Developer (SDE)'),
            ('ECE',  'Software Developer (SDE)'),
            ('ECE',  'Embedded Systems'),
            ('EEE',  'Core Electrical'),
            ('EEE',  'Software IT Support'),
            ('MECH', 'Core Mechanical'),
            ('MECH', 'Software IT Support'),
            ('CIVIL','Core Civil'),
        ]
        tracks = {}
        for code, name in tracks_data:
            t, _ = CareerTrack.objects.get_or_create(department=depts[code], name=name)
            tracks[f"{code}_{name}"] = t
        self.stdout.write('  ✓ Career Tracks')

        # ── Companies ─────────────────────────────────────────
        company_names = ['TCS', 'Infosys', 'Amazon', 'Deloitte', 'UST', 'Accenture', 'Wipro', 'Cognizant', 'L&T']
        companies = {}
        for cn in company_names:
            c, _ = Company.objects.get_or_create(name=cn)
            companies[cn] = c
        self.stdout.write('  ✓ Companies')

        # ── Skills ────────────────────────────────────────────
        skill_defs = ['Aptitude', 'Technical', 'DSA', 'SQL', 'Communication', 'Interview', 'OOP', 'DBMS']
        skills = {}
        for sn in skill_defs:
            s, _ = Skill.objects.get_or_create(name=sn)
            skills[sn] = s
        self.stdout.write('  ✓ Skills')

        # ── Assessments & Questions ───────────────────────────
        apt, _  = Assessment.objects.get_or_create(title='Initial Aptitude Test',      type='APTITUDE')
        tech, _ = Assessment.objects.get_or_create(title='Technical Core Assessment',   type='TECHNICAL')
        comm, _ = Assessment.objects.get_or_create(title='Communication & Interview',   type='COMMUNICATION')

        quant, _ = AssessmentSection.objects.get_or_create(assessment=apt,  name='Quantitative Aptitude')
        logic, _ = AssessmentSection.objects.get_or_create(assessment=apt,  name='Logical Reasoning')
        prog_sec, _ = AssessmentSection.objects.get_or_create(assessment=tech, name='Programming & DSA')
        db_sec, _   = AssessmentSection.objects.get_or_create(assessment=tech, name='DBMS & SQL')
        hr_sec, _   = AssessmentSection.objects.get_or_create(assessment=comm, name='HR & Communication')

        questions_seed = [
            (quant, "What is 15% of 200?", "20", "25", "30", "35", "C", "EASY"),
            (quant, "A train travels 120 km in 2 hours. What is its speed?", "40 km/h","50 km/h","60 km/h","70 km/h", "C", "EASY"),
            (quant, "If A=2x and B=3x, what is A+B?", "5x","4x","6x","2x", "A", "EASY"),
            (quant, "Simple interest on Rs.1000 at 5% for 2 years?", "Rs.50","Rs.100","Rs.150","Rs.200", "B", "MEDIUM"),
            (quant, "Two numbers ratio is 3:5. Sum is 64. Larger number?", "40","30","24","20", "A", "MEDIUM"),
            (logic, "Complete the series: 2, 6, 12, 20, ?", "30","28","24","32", "A", "EASY"),
            (logic, "Odd one out: Apple, Mango, Carrot, Banana", "Apple","Mango","Carrot","Banana", "C", "EASY"),
            (logic, "If all A are B, and all B are C, then all A are?", "B only","C","Neither","Cannot say", "B", "MEDIUM"),
            (prog_sec, "Which data structure uses LIFO?", "Queue","Stack","Tree","Heap", "B", "EASY"),
            (prog_sec, "Time complexity of binary search?", "O(n)","O(n²)","O(log n)","O(1)", "C", "EASY"),
            (prog_sec, "What is a linked list?", "Array in memory","Nodes with pointers","Hash table","Binary tree", "B", "EASY"),
            (prog_sec, "Which sorting algorithm is most efficient on average?", "Bubble Sort","Selection Sort","Merge Sort","Insertion Sort", "C", "MEDIUM"),
            (prog_sec, "Recursion requires?", "Loops","Base case","Global variables","External functions", "B", "MEDIUM"),
            (db_sec, "SQL command to remove a table?", "DELETE","TRUNCATE","DROP","REMOVE", "C", "EASY"),
            (db_sec, "Which JOIN returns all rows from left table?", "INNER JOIN","RIGHT JOIN","LEFT JOIN","FULL JOIN", "C", "MEDIUM"),
            (db_sec, "What does ACID stand for?", "Atomicity, Concurrency, Isolation, Durability",
             "Atomicity, Consistency, Isolation, Durability","Access, Consistency, Integrity, Durability","Atomicity, Consistency, Integrity, Data", "B", "HARD"),
            (hr_sec, "How do you handle a tight deadline?", "Panic","Prioritize tasks and communicate","Ask to extend immediately","Ignore it", "B", "EASY"),
            (hr_sec, "What is your greatest strength?", "Being lazy","Strong problem-solving skills","Nothing specific","Not sure", "B", "EASY"),
        ]

        for sec, text, a, b, c, d, correct, diff in questions_seed:
            Question.objects.get_or_create(
                section=sec, text=text,
                defaults={'option_a':a,'option_b':b,'option_c':c,'option_d':d,'correct_option':correct,'difficulty':diff}
            )
        self.stdout.write('  ✓ Questions')

        # ── Badges ────────────────────────────────────────────
        badges_data = [
            ('first-assessment',  'First Assessment',    'Completed your first assessment!',         'bi-award'),
            ('seven-day-streak',  '7 Day Streak',        'Maintained a 7-day learning streak.',       'bi-fire'),
            ('veteran-streak',    '30 Day Veteran',      'Maintained a 30-day learning streak!',      'bi-trophy'),
            ('dsa-starter',       'DSA Starter',         'Solved 10 DSA problems.',                   'bi-code-slash'),
            ('sql-master',        'SQL Master',          'Mastered SQL with Advanced level.',         'bi-database'),
            ('interview-ready',   'Interview Ready',     'Scored 80%+ in a mock interview.',          'bi-person-video3'),
            ('resume-complete',   'Resume Complete',     'Uploaded and analysed your resume.',        'bi-file-earmark-person'),
        ]
        for slug, name, desc, icon in badges_data:
            Badge.objects.get_or_create(slug=slug, defaults={'name':name,'description':desc,'icon':icon})
        self.stdout.write('  ✓ Badges')

        # ── Interview Questions ───────────────────────────────
        iq_data = [
            ('HR','Tell me about yourself.','Background, skills, career goals'),
            ('HR','What are your strengths and weaknesses?','Self-awareness, growth mindset'),
            ('HR','Why should we hire you?','Unique value, alignment'),
            ('HR','Where do you see yourself in 5 years?','Growth ambition aligned with company'),
            ('TECHNICAL','Explain polymorphism in OOP.','Overloading vs overriding with examples'),
            ('TECHNICAL','What is the time complexity of Merge Sort?','O(n log n) — divide and conquer'),
            ('TECHNICAL','Explain the difference between SQL JOIN types.','INNER, LEFT, RIGHT, FULL with examples'),
            ('TECHNICAL','What is a foreign key?','Reference integrity between tables'),
            ('COMPANY','Why do you want to work here?','Research about company, values alignment'),
            ('COMPANY','Describe a challenging project you completed.','STAR method'),
        ]
        for mode, qtext, ideal in iq_data:
            InterviewQuestion.objects.get_or_create(mode=mode, question_text=qtext, defaults={'ideal_answer_points':ideal})
        self.stdout.write('  ✓ Interview Questions')

        # ── Opportunities ─────────────────────────────────────
        opp_data = [
            ('TCS',   'TCS Ninja Campus Drive 2027',   'Software Engineer',    'CAMPUS',     6.5, 1, 10),
            ('Infosys','Infosys Campus Hiring 2027',   'Systems Engineer',     'CAMPUS',     6.0, 0, 14),
            ('Amazon','Amazon SDE Internship',          'SDE Intern',           'INTERNSHIP', 8.5, 0, 5),
            ('Wipro', 'Wipro Turbo Campus Drive',       'Software Developer',   'CAMPUS',     6.5, 0, 20),
            ('UST',   'UST Global Off-Campus',          'Associate Engineer',   'OFF_CAMPUS', 7.0, 0, 7),
        ]
        for cname, title, role, otype, cgpa, backlogs, days in opp_data:
            Opportunity.objects.get_or_create(
                company=companies.get(cname, Company.objects.first()),
                title=title,
                defaults={
                    'role': role, 'type': otype, 'cgpa_cutoff': cgpa,
                    'allowed_backlogs': backlogs,
                    'deadline': timezone.now() + datetime.timedelta(days=days),
                    'is_verified': True, 'status': 'OPEN'
                }
            )
        self.stdout.write('  ✓ Opportunities')

        # ── Demo Students ─────────────────────────────────────
        demo_students = [
            ('arjun.nair@demo.com',  'Arjun', 'Nair',  'CSE',  4, 8.9, 0, 'Software Developer',    'CSE_Software Developer (SDE)'),
            ('rahul.kumar@demo.com', 'Rahul', 'Kumar', 'CSE',  3, 7.4, 0, 'Data Scientist',         'CSE_Data Science / ML'),
            ('ananya.r@demo.com',    'Ananya','R',     'ECE',  3, 8.1, 0, 'Embedded Engineer',      'ECE_Embedded Systems'),
            ('meera.s@demo.com',     'Meera', 'S',     'MECH', 4, 7.8, 0, 'Core Mechanical',        'MECH_Core Mechanical'),
        ]
        demo_company_map = {
            'arjun.nair@demo.com':  ['TCS','Infosys','Amazon','Deloitte','UST'],
            'rahul.kumar@demo.com': ['Amazon','Deloitte','Wipro'],
            'ananya.r@demo.com':    ['TCS','Infosys','Cognizant'],
            'meera.s@demo.com':     ['L&T','Infosys','TCS'],
        }
        demo_skills = {
            'arjun.nair@demo.com':  {'Aptitude':78,'Technical':65,'DSA':48,'SQL':52,'Communication':71,'Interview':55},
            'rahul.kumar@demo.com': {'Aptitude':60,'Technical':82,'DSA':76,'SQL':68,'Communication':42,'Interview':48},
            'ananya.r@demo.com':    {'Aptitude':72,'Technical':74,'DSA':55,'Communication':68,'Interview':60},
            'meera.s@demo.com':     {'Aptitude':65,'Technical':58,'Communication':80,'Interview':70},
        }

        for email, fname, lname, dept_code, year, cgpa, backlogs, goal, track_key in demo_students:
            if User.objects.filter(username=email).exists():
                self.stdout.write(f'  • Skipping existing: {email}')
                continue

            user = User.objects.create_user(
                username=email, email=email, password='demo1234',
                first_name=fname, last_name=lname, role='STUDENT'
            )
            profile = StudentProfile.objects.create(
                user=user,
                department=depts.get(dept_code),
                year=year, cgpa=cgpa, backlogs=backlogs,
                career_goal=goal,
                career_track=tracks.get(track_key),
                onboarding_completed=True,
            )
            # Companies
            for cname in demo_company_map.get(email, []):
                if cname in companies:
                    profile.target_companies.add(companies[cname])

            # Skill Profiles
            for sname, mastery in demo_skills.get(email, {}).items():
                if sname in skills:
                    level = 'ADVANCED' if mastery >= 75 else ('NORMAL' if mastery >= 45 else 'BEGINNER')
                    SkillProfile.objects.create(
                        student=profile, skill=skills[sname],
                        level=level, mastery_percentage=mastery,
                        trend=random.choice(['Improving','Stable','Improving'])
                    )

            # Readiness
            total_mastery = sum(demo_skills.get(email, {}).values())
            count = len(demo_skills.get(email, {}))
            profile.overall_readiness = int(total_mastery / count) if count else 0
            profile.save()

            # Gamification
            gami = Gamification.objects.create(
                student=profile,
                xp=random.randint(500, 3000),
                streak=random.randint(3, 21),
                last_active_date=timezone.now().date(),
            )

            # Notifications
            Notification.objects.create(user=user, title='Welcome to HireU!',
                message='Take your initial assessments to build your Skill Passport.', type='INFO')

            self.stdout.write(f'  ✓ Demo student: {fname} {lname} ({email}) / demo1234')

        # ── Officer Account ───────────────────────────────────
        if not User.objects.filter(username='officer@hireu.com').exists():
            User.objects.create_user(
                username='officer@hireu.com', email='officer@hireu.com',
                password='officer123', first_name='Placement', last_name='Officer', role='OFFICER'
            )
            self.stdout.write('  ✓ Officer: officer@hireu.com / officer123')
        else:
            self.stdout.write('  • Officer account already exists')

        self.stdout.write(self.style.SUCCESS('\n✅ HireU seeded successfully!\n'))
        self.stdout.write('  Student accounts (all pass: demo1234):')
        self.stdout.write('    arjun.nair@demo.com   — CSE, Software Developer')
        self.stdout.write('    rahul.kumar@demo.com  — CSE, Data Scientist')
        self.stdout.write('    ananya.r@demo.com     — ECE, Embedded Engineer')
        self.stdout.write('    meera.s@demo.com      — MECH, Core Mechanical')
        self.stdout.write('  Officer: officer@hireu.com / officer123')
