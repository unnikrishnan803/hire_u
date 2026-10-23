from django.core.management.base import BaseCommand
from assessment.models import Assessment, AssessmentSection, Question

class Command(BaseCommand):
    help = 'Seeds initial Assessments and Questions'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding assessments...")

        aptitude, _ = Assessment.objects.get_or_create(title="Initial Aptitude Test", type="APTITUDE")
        tech, _ = Assessment.objects.get_or_create(title="Technical Core Assessment", type="TECHNICAL")
        comm, _ = Assessment.objects.get_or_create(title="Communication Readiness", type="COMMUNICATION")

        # Sections
        quant_sec, _ = AssessmentSection.objects.get_or_create(assessment=aptitude, name="Quantitative Aptitude")
        logic_sec, _ = AssessmentSection.objects.get_or_create(assessment=aptitude, name="Logical Reasoning")
        
        prog_sec, _ = AssessmentSection.objects.get_or_create(assessment=tech, name="Programming & DSA")
        dbms_sec, _ = AssessmentSection.objects.get_or_create(assessment=tech, name="DBMS & SQL")
        
        hr_sec, _ = AssessmentSection.objects.get_or_create(assessment=comm, name="HR & Situational")

        # Questions
        questions = [
            (quant_sec, "What is 15% of 200?", "20", "25", "30", "35", "C"),
            (quant_sec, "If a train travels 60km in 45 mins, what is its speed in km/hr?", "60", "75", "80", "90", "C"),
            (logic_sec, "Complete the series: 2, 6, 12, 20, ?", "30", "28", "24", "32", "A"),
            (prog_sec, "Which data structure uses LIFO?", "Queue", "Stack", "Tree", "Graph", "B"),
            (prog_sec, "What is the time complexity of binary search?", "O(n)", "O(n log n)", "O(log n)", "O(1)", "C"),
            (dbms_sec, "Which SQL command is used to remove a table?", "DELETE", "DROP", "TRUNCATE", "REMOVE", "B"),
            (hr_sec, "How do you handle a tight deadline?", "Panic", "Prioritize tasks", "Ask for extension immediately", "Ignore it", "B"),
        ]

        for sec, text, a, b, c, d, correct in questions:
            Question.objects.get_or_create(
                section=sec, text=text,
                defaults={
                    'option_a': a, 'option_b': b, 'option_c': c, 'option_d': d, 'correct_option': correct
                }
            )

        self.stdout.write(self.style.SUCCESS("Assessments seeded successfully!"))
