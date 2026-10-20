from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from ..models import UserProfile


class UserProfileViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )

    def test_profile_view_creates_profile_if_missing(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:profile'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_profile_view_updates_phone_number_and_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:profile'),
            {'phone_number': '1234567890'},
        )

        profile = UserProfile.objects.get(user=self.user)

        self.assertRedirects(response, reverse('expenses:profile'))
        self.assertEqual(profile.phone_number, '1234567890')

    def test_profile_view_shows_success_message_after_update(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:profile'),
            {'phone_number': '1234567890'},
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, reverse('expenses:profile'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Profile updated successfully.')
        self.assertEqual(messages[0].tags, 'success')

    def test_profile_view_shows_error_message_for_empty_phone_number(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:profile'),
            {'phone_number': ''},
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Please correct the profile errors below.',
        )
        self.assertEqual(messages[0].tags, 'error')
