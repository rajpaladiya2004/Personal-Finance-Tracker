from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Category, Notification


class CategoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.other_user = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='student', password='testpass123')

    def test_add_category_creates_category_for_logged_in_user(self):
        response = self.client.post(reverse('expenses:add_category'), {'name': 'Food'})

        self.assertRedirects(response, reverse('expenses:add_category'))
        self.assertTrue(Category.objects.filter(user=self.user, name='Food').exists())

    def test_add_category_creates_notification(self):
        self.client.post(reverse('expenses:add_category'), {'name': 'Food'})

        self.assertTrue(
            Notification.objects.filter(user=self.user, title='New category added').exists()
        )

    def test_duplicate_category_name_is_rejected_case_insensitively(self):
        Category.objects.create(user=self.user, name='Food')

        response = self.client.post(reverse('expenses:add_category'), {'name': 'food'})

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertEqual(Category.objects.filter(user=self.user).count(), 1)

    def test_same_category_name_is_allowed_for_different_users(self):
        Category.objects.create(user=self.other_user, name='Food')

        response = self.client.post(reverse('expenses:add_category'), {'name': 'Food'})

        self.assertRedirects(response, reverse('expenses:add_category'))
        self.assertTrue(Category.objects.filter(user=self.user, name='Food').exists())

    def test_empty_category_name_is_rejected(self):
        response = self.client.post(reverse('expenses:add_category'), {'name': ''})

        self.assertEqual(response.status_code, 200)
        self.assertIn('name', response.context['form'].errors)
        self.assertFalse(Category.objects.filter(user=self.user).exists())

    def test_category_list_shows_only_own_categories(self):
        Category.objects.create(user=self.user, name='Food')
        Category.objects.create(user=self.other_user, name='Secret')

        response = self.client.get(reverse('expenses:category_list'))

        self.assertContains(response, 'Food')
        self.assertNotContains(response, 'Secret')
