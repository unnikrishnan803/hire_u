from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, StudentProfile
from career.models import Skill, SkillProfile

class CareerAndRoadmapTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='careerstudent@hireu.com',
            email='careerstudent@hireu.com',
            password='Password123',
            role='STUDENT'
        )
        self.profile = StudentProfile.objects.create(
            user=self.user,
            onboarding_completed=True,
            career_goal='Full Stack Developer'
        )

        # Set up skill profiles with distinct masteries
        self.sk_apt, _ = Skill.objects.get_or_create(name='Aptitude', defaults={'category': 'Aptitude'})
        self.sk_tech, _ = Skill.objects.get_or_create(name='Technical', defaults={'category': 'Technical'})
        self.sk_dsa, _ = Skill.objects.get_or_create(name='Programming / DSA', defaults={'category': 'Technical'})
        self.sk_comm, _ = Skill.objects.get_or_create(name='Communication', defaults={'category': 'Soft Skill'})

        # Aptitude: 80% (Advanced)
        SkillProfile.objects.create(student=self.profile, skill=self.sk_apt, mastery_percentage=80, level='ADVANCED')
        # Technical: 60% (Normal - moderate gap)
        SkillProfile.objects.create(student=self.profile, skill=self.sk_tech, mastery_percentage=60, level='NORMAL')
        # DSA: 35% (Beginner - high priority gap)
        SkillProfile.objects.create(student=self.profile, skill=self.sk_dsa, mastery_percentage=35, level='BEGINNER')
        # Communication: 25% (Beginner - high priority gap)
        SkillProfile.objects.create(student=self.profile, skill=self.sk_comm, mastery_percentage=25, level='BEGINNER')

    def test_skill_passport_page_and_rule_based_gap_analysis(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('skill_passport'))
        self.assertEqual(response.status_code, 200)

        # High priority gaps should contain DSA and Communication (< 45%)
        high_gaps = [g['name'] for g in response.context['high_priority_gaps']]
        self.assertIn('Programming / DSA', high_gaps)
        self.assertIn('Communication', high_gaps)

        # Moderate gaps should contain Technical (60%)
        mod_gaps = [g['name'] for g in response.context['moderate_gaps']]
        self.assertIn('Technical', mod_gaps)

        # Mastered skills should contain Aptitude (80%)
        mastered = [s['name'] for s in response.context['mastered_skills']]
        self.assertIn('Aptitude', mastered)

    def test_career_roadmap_view_and_milestones(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('career_roadmap'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('phases', response.context)
        phases = response.context['phases']
        self.assertEqual(len(phases), 4)

        # Phase 1 corresponds to Aptitude (score 80 >= 70, so COMPLETED)
        self.assertEqual(phases[0]['number'], 1)
        self.assertEqual(phases[0]['status'], 'COMPLETED')

        # Phase 2 corresponds to Technical (score 60 > 0, so IN_PROGRESS)
        self.assertEqual(phases[1]['number'], 2)
        self.assertEqual(phases[1]['status'], 'IN_PROGRESS')
