from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from ..models import ContactMessage, Notification


class InfoPagesTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='student', password='testpass123')

    def test_info_pages_render_for_logged_in_user(self):
        self.client.login(username='student', password='testpass123')

        for name in ('help_support', 'terms_conditions', 'privacy_policy', 'about_us', 'faq'):
            with self.subTest(page=name):
                response = self.client.get(reverse(f'expenses:{name}'))
                self.assertEqual(response.status_code, 200)

    def test_info_pages_redirect_anonymous_users(self):
        response = self.client.get(reverse('expenses:faq'))

        self.assertEqual(response.status_code, 302)


class ContactTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.client.login(username='student', password='testpass123')

    def test_contact_message_is_saved_for_user(self):
        response = self.client.post(
            reverse('expenses:contact_us'),
            {'name': 'Student', 'email': 's@example.com', 'subject': 'Hi', 'message': 'Hello'},
        )

        self.assertRedirects(response, reverse('expenses:contact_us'))
        self.assertTrue(ContactMessage.objects.filter(user=self.user, subject='Hi').exists())

    def test_invalid_contact_message_shows_error(self):
        response = self.client.post(reverse('expenses:contact_us'), {'name': 'Student'})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(messages[0]), 'Please correct the errors below.')
        self.assertFalse(ContactMessage.objects.exists())


class NotificationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.client.login(username='student', password='testpass123')

    def test_notifications_page_lists_own_notifications(self):
        Notification.objects.create(user=self.user, title='Notice', message='Hello notice')

        response = self.client.get(reverse('expenses:notifications'))

        self.assertContains(response, 'Hello notice')

    def test_notifications_are_paginated_by_ten(self):
        for index in range(11):
            Notification.objects.create(user=self.user, title=f'N{index}', message='m')

        first = self.client.get(reverse('expenses:notifications'))
        second = self.client.get(reverse('expenses:notifications') + '?page=2')

        self.assertEqual(len(first.context['notifications']), 10)
        self.assertEqual(len(second.context['notifications']), 1)
