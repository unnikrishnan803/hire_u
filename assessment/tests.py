from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User, StudentProfile, Department
from assessment.models import Assessment, AssessmentSection, Question, AssessmentAttempt, Answer
from career.models import Skill, SkillProfile
from learning.models import DailyTask

class AssessmentTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Student 1
        self.user1 = User.objects.create_user(
            username='student1@hireu.com',
            email='student1@hireu.com',
            password='Password123',
            role='STUDENT'
        )
        self.profile1 = StudentProfile.objects.create(
            user=self.user1, onboarding_completed=True, career_goal='Software Engineer'
        )

        # Student 2 (for access control test)
        self.user2 = User.objects.create_user(
            username='student2@hireu.com',
            email='student2@hireu.com',
            password='Password123',
            role='STUDENT'
        )
        self.profile2 = StudentProfile.objects.create(
            user=self.user2, onboarding_completed=True
        )

        # Create Aptitude Assessment and Section
        self.assessment = Assessment.objects.create(
            title='Aptitude Assessment',
            type='APTITUDE',
            is_active=True
        )
        self.section = AssessmentSection.objects.create(
            assessment=self.assessment,
            name='Quantitative Aptitude'
        )

        # Create 4 Questions with verified answers
        self.q1 = Question.objects.create(
            section=self.section, text='Question 1 text',
            option_a='Opt A', option_b='Opt B', option_c='Opt C', option_d='Opt D',
            correct_option='A', difficulty='EASY'
        )
        self.q2 = Question.objects.create(
            section=self.section, text='Question 2 text',
            option_a='Opt A', option_b='Opt B', option_c='Opt C', option_d='Opt D',
            correct_option='B', difficulty='MEDIUM'
        )
        self.q3 = Question.objects.create(
            section=self.section, text='Question 3 text',
            option_a='Opt A', option_b='Opt B', option_c='Opt C', option_d='Opt D',
            correct_option='C', difficulty='MEDIUM'
        )
        self.q4 = Question.objects.create(
            section=self.section, text='Question 4 text',
            option_a='Opt A', option_b='Opt B', option_c='Opt C', option_d='Opt D',
            correct_option='D', difficulty='HARD'
        )

    def test_assessment_list_page(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('assessments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aptitude Assessment')

    def test_take_assessment_loads_questions_from_db(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('take_assessment', args=[self.assessment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Question 1 text')
        self.assertContains(response, 'Question 2 text')

    def test_assessment_scoring_and_result_persistence(self):
        self.client.force_login(self.user1)
        # Answer Q1 correct ('A'), Q2 correct ('B'), Q3 incorrect ('A' instead of 'C'), Q4 skipped
        post_data = {
            'question_ids': [self.q1.id, self.q2.id, self.q3.id, self.q4.id],
            f'question_{self.q1.id}': 'A',  # Correct
            f'question_{self.q2.id}': 'B',  # Correct
            f'question_{self.q3.id}': 'A',  # Incorrect (correct is C)
            # Q4 not in POST (skipped)
        }
        response = self.client.post(reverse('take_assessment', args=[self.assessment.id]), post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check Attempt created and scored: 2 out of 4 = 50%
        self.assertEqual(AssessmentAttempt.objects.filter(user=self.user1).count(), 1)
        attempt = AssessmentAttempt.objects.get(user=self.user1)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.max_score, 4)

        # Check Answer objects persisted
        answers = Answer.objects.filter(attempt=attempt)
        self.assertEqual(answers.count(), 4)
        ans1 = answers.get(question=self.q1)
        self.assertTrue(ans1.is_correct)
        self.assertEqual(ans1.selected_option, 'A')

        ans3 = answers.get(question=self.q3)
        self.assertFalse(ans3.is_correct)
        self.assertEqual(ans3.selected_option, 'A')

        ans4 = answers.get(question=self.q4)
        self.assertFalse(ans4.is_correct)
        self.assertIsNone(ans4.selected_option)

        # Check SkillProfile updated: 50% -> NORMAL level
        sp = SkillProfile.objects.get(student=self.profile1, skill__name='Aptitude')
        self.assertEqual(sp.mastery_percentage, 50)
        self.assertEqual(sp.level, 'NORMAL')

        # Check overall readiness recalculated
        self.profile1.refresh_from_db()
        self.assertGreater(self.profile1.overall_readiness, 0)

    def test_reassessment_updates_skill_level_with_weighted_history(self):
        self.client.force_login(self.user1)
        # First attempt: score 100% (4/4) -> mastery 100%, level ADVANCED
        post_data_1 = {
            'question_ids': [self.q1.id, self.q2.id, self.q3.id, self.q4.id],
            f'question_{self.q1.id}': 'A',
            f'question_{self.q2.id}': 'B',
            f'question_{self.q3.id}': 'C',
            f'question_{self.q4.id}': 'D',
        }
        self.client.post(reverse('take_assessment', args=[self.assessment.id]), post_data_1)
        sp = SkillProfile.objects.get(student=self.profile1, skill__name='Aptitude')
        self.assertEqual(sp.mastery_percentage, 100)
        self.assertEqual(sp.level, 'ADVANCED')

        # Reassessment: score 0% (0/4)
        # Weighted formula: new = round(0 * 0.6 + 100 * 0.4) = 40% -> BEGINNER level
        post_data_2 = {
            'question_ids': [self.q1.id, self.q2.id, self.q3.id, self.q4.id],
            f'question_{self.q1.id}': 'B',
            f'question_{self.q2.id}': 'A',
            f'question_{self.q3.id}': 'D',
            f'question_{self.q4.id}': 'C',
        }
        self.client.post(reverse('take_assessment', args=[self.assessment.id]), post_data_2)
        sp.refresh_from_db()
        self.assertEqual(sp.mastery_percentage, 40)
        self.assertEqual(sp.level, 'BEGINNER')
        self.assertEqual(sp.trend, 'Declining')

    def test_access_control_cannot_access_other_students_results(self):
        # Create an attempt belonging to student 1
        attempt = AssessmentAttempt.objects.create(
            user=self.user1, assessment=self.assessment, score=3, max_score=4
        )

        # Student 1 can access
        self.client.force_login(self.user1)
        res_ok = self.client.get(reverse('assessment_result', args=[attempt.id]))
        self.assertEqual(res_ok.status_code, 200)

        # Student 2 CANNOT access student 1's attempt (returns 404)
        self.client.force_login(self.user2)
        res_denied = self.client.get(reverse('assessment_result', args=[attempt.id]))
        self.assertEqual(res_denied.status_code, 404)

    def test_daily_task_completion_ajax(self):
        self.client.force_login(self.user1)
        task = DailyTask.objects.create(
            student=self.profile1,
            title='Daily Arrays Practice',
            skill_area='DSA',
            difficulty='EASY',
            estimated_minutes=15,
            xp_reward=30,
            date=timezone.now().date()
        )
        response = self.client.post(reverse('complete_task', args=[task.id]))
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, 'COMPLETED')
