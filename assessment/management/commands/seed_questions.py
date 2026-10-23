from django.core.management.base import BaseCommand
from assessment.models import Assessment, AssessmentSection, Question

class Command(BaseCommand):
    help = 'Seed verified questions for Aptitude, Technical, and Communication assessments'

    def handle(self, *args, **kwargs):
        # 1. Aptitude Test
        apt_test, _ = Assessment.objects.get_or_create(
            title='Initial Aptitude Test',
            defaults={'type': 'APTITUDE', 'description': 'Quantitative, Logical Reasoning, and Numerical Ability', 'is_active': True}
        )
        quant_sec, _ = AssessmentSection.objects.get_or_create(assessment=apt_test, name='Quantitative Aptitude')
        logical_sec, _ = AssessmentSection.objects.get_or_create(assessment=apt_test, name='Logical Reasoning')

        # 2. Technical Core Assessment
        tech_test, _ = Assessment.objects.get_or_create(
            title='Technical Core Assessment',
            defaults={'type': 'TECHNICAL', 'description': 'Programming, Data Structures, Algorithms, and DBMS', 'is_active': True}
        )
        dsa_sec, _ = AssessmentSection.objects.get_or_create(assessment=tech_test, name='Programming & DSA')
        dbms_sec, _ = AssessmentSection.objects.get_or_create(assessment=tech_test, name='DBMS & SQL')

        # 3. Communication Assessment
        comm_test, _ = Assessment.objects.get_or_create(
            title='Communication & Interview',
            defaults={'type': 'COMMUNICATION', 'description': 'Business Communication, HR Questions, and Situational Judgment', 'is_active': True}
        )
        comm_sec, _ = AssessmentSection.objects.get_or_create(assessment=comm_test, name='HR & Communication')

        questions_data = [
            # Quantitative Aptitude
            (quant_sec, "A train running at the speed of 60 km/hr crosses a pole in 9 seconds. What is the length of the train?",
             "120 metres", "180 metres", "324 metres", "150 metres", "D",
             "Speed = 60 * (5/18) = 50/3 m/s. Length = Speed * Time = (50/3) * 9 = 150 metres.", "EASY"),
            (quant_sec, "If a shopkeeper sells an article at Rs. 300 gaining a profit of 20%, what was its cost price?",
             "Rs. 240", "Rs. 250", "Rs. 260", "Rs. 280", "B",
             "Cost Price = Selling Price / (1 + Profit%) = 300 / 1.20 = Rs. 250.", "EASY"),
            (quant_sec, "Two pipes A and B can fill a tank in 20 and 30 minutes respectively. If both pipes are opened together, the time taken to fill the tank is:",
             "50 minutes", "12 minutes", "25 minutes", "15 minutes", "B",
             "Part filled in 1 min = (1/20) + (1/30) = 5/60 = 1/12. So time taken is 12 minutes.", "MEDIUM"),
            (quant_sec, "In a lottery, there are 10 prizes and 25 blanks. A lottery is drawn at random. What is the probability of getting a prize?",
             "1/10", "2/5", "2/7", "5/7", "C",
             "Total outcomes = 10 + 25 = 35. Favorable outcomes = 10. Probability = 10/35 = 2/7.", "MEDIUM"),
            
            # Logical Reasoning
            (logical_sec, "Pointing to a photograph of a boy, Suresh said, 'He is the son of the only son of my mother.' How is Suresh related to that boy?",
             "Brother", "Uncle", "Cousin", "Father", "D",
             "The only son of Suresh's mother is Suresh himself. So the boy is Suresh's son. Suresh is his father.", "EASY"),
            (logical_sec, "Find the next number in the sequence: 3, 7, 15, 31, 63, ?",
             "95", "127", "128", "126", "B",
             "Each number follows 2n + 1: 63 * 2 + 1 = 127.", "MEDIUM"),
            (logical_sec, "In a certain code, 'COMPUTER' is written as 'RFUVQNPC'. How is 'MEDICINE' written in that code?",
             "EOJDJEFM", "EOJDEJFM", "MFEJDJOE", "MFEDJJOE", "A",
             "The first and last letters are swapped and other letters are shifted forward by 1.", "HARD"),

            # Programming & DSA
            (dsa_sec, "What is the worst-case time complexity of searching an element in a balanced Binary Search Tree (AVL tree) with n nodes?",
             "O(1)", "O(log n)", "O(n)", "O(n log n)", "B",
             "Balanced binary search trees maintain height at O(log n), so lookups take worst-case O(log n).", "EASY"),
            (dsa_sec, "Which data structure is fundamentally used for Breadth First Search (BFS) graph traversal?",
             "Stack", "Queue", "Heap", "Priority Queue", "B",
             "BFS traverses level-by-level in FIFO order, implemented with a Queue.", "EASY"),
            (dsa_sec, "What happens when an array of size n is rotated to the right by k positions where k = n?",
             "Elements reverse order", "Array remains identical", "First and last elements swap", "Array shifts by 1", "B",
             "Rotating by n positions in an array of length n results in the exact same original array.", "MEDIUM"),
            (dsa_sec, "Which algorithmic paradigm does Merge Sort utilize?",
             "Dynamic Programming", "Greedy Algorithm", "Divide and Conquer", "Backtracking", "C",
             "Merge Sort divides the array into halves, sorts them recursively, and merges them.", "EASY"),

            # DBMS & SQL
            (dbms_sec, "Which SQL constraint ensures that all values in a column are distinct and not null?",
             "UNIQUE", "CHECK", "FOREIGN KEY", "PRIMARY KEY", "D",
             "A PRIMARY KEY constraint uniquely identifies each record and does not allow NULL values.", "EASY"),
            (dbms_sec, "Which normal form deals with the elimination of transitive functional dependencies?",
             "First Normal Form (1NF)", "Second Normal Form (2NF)", "Third Normal Form (3NF)", "Boyce-Codd Normal Form (BCNF)", "C",
             "3NF requires the relation to be in 2NF and eliminate transitive dependencies (non-prime attributes depending on non-prime attributes).", "MEDIUM"),
            (dbms_sec, "In database transactions, which ACID property ensures that all operations succeed or none are applied?",
             "Atomicity", "Consistency", "Isolation", "Durability", "A",
             "Atomicity guarantees 'all-or-nothing' execution of transaction steps.", "EASY"),

            # Communication & Interview
            (comm_sec, "What does the 'STAR' technique stand for in answering behavioral interview questions?",
             "Situation, Task, Action, Result", "Strategy, Timing, Attitude, Response", "Skill, Target, Achievement, Review", "Speaking, Tone, Articulation, Resonance", "A",
             "STAR stands for Situation, Task, Action, and Result — the gold standard for behavioral interviews.", "EASY"),
            (comm_sec, "When a recruiter asks 'What is your greatest weakness?', what is the most professional response strategy?",
             "State that you have no real weaknesses.",
             "Mention a personal flaw completely irrelevant to jobs.",
             "Mention a genuine technical/professional area you are actively improving and describe steps taken.",
             "Blame past professors or college team members.", "C",
             "Self-awareness and demonstrable proactive remediation is what interviewers look for.", "MEDIUM"),
            (comm_sec, "In professional email correspondence, when should 'BCC' (Blind Carbon Copy) primarily be used?",
             "To send email to your direct manager.",
             "To protect recipients' email privacy when emailing large external groups.",
             "To reply to all coworkers on a project thread.",
             "To demand urgent feedback.", "B",
             "BCC conceals recipient addresses from each other when distributing broad notices.", "EASY"),
            (comm_sec, "If two teammates disagree on which framework to use for a project, the best conflict resolution approach is:",
             "Avoid discussing the topic and work separately.",
             "Compare both frameworks against clear objective technical criteria, team familiarity, and project deadlines.",
             "Let the most vocal person decide immediately without testing.",
             "Escalate directly to executive management without attempting peer discussion.", "B",
             "Objective criteria comparison fosters consensus and sound engineering judgment.", "MEDIUM"),
        ]

        created_count = 0
        for sec, text, a, b, c, d, correct, explanation, diff in questions_data:
            if not Question.objects.filter(section=sec, text=text).exists():
                Question.objects.create(
                    section=sec,
                    text=text,
                    option_a=a,
                    option_b=b,
                    option_c=c,
                    option_d=d,
                    correct_option=correct,
                    explanation=explanation,
                    difficulty=diff
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} new questions!'))
