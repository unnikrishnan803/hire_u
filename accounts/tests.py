from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User, StudentProfile, Department, CareerTrack
from companies.models import Company

class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_valid_registration(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Test',
            'last_name': 'Student',
            'email': 'teststudent@example.com',
            'password': 'SecurePassword123!',
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='teststudent@example.com').exists())
        user = User.objects.get(email='teststudent@example.com')
        self.assertEqual(user.role, 'STUDENT')
        self.assertTrue(hasattr(user, 'student_profile'))
        self.assertFalse(user.student_profile.onboarding_completed)

    def test_registration_duplicate_email(self):
        User.objects.create_user(
            username='dup@example.com',
            email='dup@example.com',
            password='Password123'
        )
        response = self.client.post(reverse('register'), {
            'first_name': 'Dup',
            'last_name': 'User',
            'email': 'dup@example.com',
            'password': 'NewPassword123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='dup@example.com').count(), 1)

    def test_registration_short_password(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Short',
            'last_name': 'Pass',
            'email': 'shortpass@example.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='shortpass@example.com').exists())

    def test_registration_invalid_email(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Bad',
            'last_name': 'Email',
            'email': 'not-an-email',
            'password': 'Password123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='not-an-email').exists())


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='authstudent@example.com',
            email='authstudent@example.com',
            password='TestPassword123',
            role='STUDENT'
        )
        self.profile = StudentProfile.objects.create(user=self.user)

    def test_login_and_logout(self):
        # Successful login
        login_resp = self.client.post(reverse('login'), {
            'email': 'authstudent@example.com',
            'password': 'TestPassword123'
        }, follow=True)
        self.assertEqual(login_resp.status_code, 200)
        self.assertTrue('_auth_user_id' in self.client.session)

        # Successful logout
        logout_resp = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_resp.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'authstudent@example.com',
            'password': 'WrongPassword!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_protected_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)


class ProfileTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='student1@example.com',
            email='student1@example.com',
            password='Password123',
            role='STUDENT'
        )
        self.profile = StudentProfile.objects.create(user=self.user)
        self.dept = Department.objects.create(name='Mechanical Engineering', code='MECH')
        self.track = CareerTrack.objects.create(department=self.dept, name='Robotics & Automation')
        
        for i in range(7):
            Company.objects.create(name=f'Company_{i}')

    def test_onboarding_and_independent_career_goal(self):
        self.client.force_login(self.user)
        companies = list(Company.objects.values_list('id', flat=True)[:4])
        
        # Dept is Mechanical, but Career Goal is Software Engineer (demonstrating independence)
        response = self.client.post(reverse('onboarding'), {
            'department': self.dept.id,
            'year': 3,
            'cgpa': 8.75,
            'backlogs': 0,
            'career_goal': 'Full Stack Software Engineer',
            'career_track': self.track.id,
            'companies': companies,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.onboarding_completed)
        self.assertEqual(self.profile.department.code, 'MECH')
        self.assertEqual(self.profile.career_goal, 'Full Stack Software Engineer')
        self.assertEqual(self.profile.target_companies.count(), 4)

    def test_target_company_limit_and_deduplication(self):
        self.client.force_login(self.user)
        all_comp_ids = list(Company.objects.values_list('id', flat=True))
        # Submit 7 company IDs with duplicates
        submitted_ids = [all_comp_ids[0], all_comp_ids[0], all_comp_ids[1], all_comp_ids[2], all_comp_ids[3], all_comp_ids[4], all_comp_ids[5]]
        
        response = self.client.post(reverse('edit_profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone': '9876543210',
            'department': self.dept.id,
            'year': 4,
            'cgpa': 9.1,
            'backlogs': 0,
            'career_goal': 'AI Engineer',
            'companies': submitted_ids,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        # Must be capped at max 5 and contain no duplicates
        self.assertLessEqual(self.profile.target_companies.count(), 5)
        self.assertEqual(len(set(self.profile.target_companies.values_list('id', flat=True))), self.profile.target_companies.count())

    def test_view_and_edit_profile(self):
        self.client.force_login(self.user)
        # View profile
        view_resp = self.client.get(reverse('profile'))
        self.assertEqual(view_resp.status_code, 200)
        self.assertContains(view_resp, self.user.email)

        # Edit profile
        edit_resp = self.client.post(reverse('edit_profile'), {
            'first_name': 'Alice',
            'last_name': 'Wonderland',
            'phone': '1234567890',
            'department': self.dept.id,
            'year': 2,
            'cgpa': 8.2,
            'backlogs': 1,
            'career_goal': 'Cloud DevOps Engineer',
            'companies': [],
        }, follow=True)
        self.assertEqual(edit_resp.status_code, 200)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Alice')
        self.assertEqual(self.user.last_name, 'Wonderland')
        self.assertEqual(self.profile.career_goal, 'Cloud DevOps Engineer')
        self.assertEqual(self.profile.backlogs, 1)

    def test_unauthenticated_cannot_access_profile(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_view_authenticated(self):
        self.profile.onboarding_completed = True
        self.profile.target_companies.set(Company.objects.all()[:3])
        self.profile.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Good')
        self.assertIn('companies', response.context)

