from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from ..models import UserProfile


class LoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
        )

    def test_login_uses_built_in_view_and_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('expenses:login'),
            {'username': 'student', 'password': 'testpass123'},
        )

        self.assertRedirects(response, reverse('expenses:dashboard'))

    def test_login_with_email_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('expenses:login'),
            {'username': 'student@example.com', 'password': 'testpass123'},
        )

        self.assertRedirects(response, reverse('expenses:dashboard'))

    def test_login_with_wrong_password_shows_form_error(self):
        response = self.client.post(
            reverse('expenses:login'),
            {'username': 'student', 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_with_unknown_user_is_rejected(self):
        response = self.client.post(
            reverse('expenses:login'),
            {'username': 'nobody', 'password': 'testpass123'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_redirects_to_login_page(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(reverse('expenses:logout'))

        self.assertRedirects(response, reverse('expenses:login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class AccessControlTests(TestCase):
    def test_protected_pages_redirect_anonymous_users_to_login(self):
        protected_routes = [
            'expenses:dashboard',
            'expenses:transaction_list',
            'expenses:add_transaction',
            'expenses:category_list',
            'expenses:add_category',
            'expenses:profile',
            'expenses:notifications',
        ]

        for name in protected_routes:
            with self.subTest(route=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'/login/?next={url}',
                    fetch_redirect_response=False,
                )

    def test_home_shows_landing_page_to_anonymous_users(self):
        response = self.client.get(reverse('expenses:home'))

        self.assertEqual(response.status_code, 200)

    def test_home_redirects_logged_in_user_to_dashboard(self):
        User.objects.create_user(username='student', password='testpass123')
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:home'))

        self.assertRedirects(response, reverse('expenses:dashboard'))


class RegistrationTests(TestCase):
    def test_register_page_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse('expenses:register'),
            {
                'username': 'newstudent',
                'email': 'newstudent@example.com',
                'password1': 'testpass12345',
                'password2': 'testpass12345',
            },
        )

        self.assertRedirects(response, reverse('expenses:login'))
        self.assertTrue(User.objects.filter(username='newstudent').exists())
        self.assertEqual(
            User.objects.get(username='newstudent').email,
            'newstudent@example.com',
        )

    def test_register_page_shows_error_message_for_invalid_data(self):
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass12345',
        )

        response = self.client.post(
            reverse('expenses:register'),
            {
                'username': 'existinguser',
                'email': 'existing@example.com',
                'password1': 'testpass12345',
                'password2': 'differentpass123',
            },
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Please correct the registration errors below.',
        )
        self.assertEqual(messages[0].tags, 'error')

    def test_register_does_not_create_user_when_invalid(self):
        self.client.post(
            reverse('expenses:register'),
            {
                'username': 'baduser',
                'email': 'bad@example.com',
                'password1': 'testpass12345',
                'password2': 'differentpass123',
            },
        )

        self.assertFalse(User.objects.filter(username='baduser').exists())

    def test_register_redirects_logged_in_user_to_dashboard(self):
        User.objects.create_user(username='student', password='testpass123')
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:register'))

        self.assertRedirects(response, reverse('expenses:dashboard'))


class DeleteAccountViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )
        UserProfile.objects.create(user=self.user, phone_number='1234567890')

    def test_delete_account_removes_profile_and_user_then_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(reverse('expenses:delete_account'))

        self.assertRedirects(response, reverse('expenses:login'))
        self.assertFalse(UserProfile.objects.filter(user=self.user).exists())
        self.assertFalse(get_user_model().objects.filter(username='student').exists())

    def test_delete_account_routes_render_and_submit(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:delete_account'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('expenses:delete_account_confirm'))
        self.assertRedirects(response, reverse('expenses:login'))

    def test_get_request_does_not_delete_account(self):
        self.client.login(username='student', password='testpass123')

        self.client.get(reverse('expenses:delete_account'))

        self.assertTrue(get_user_model().objects.filter(username='student').exists())
