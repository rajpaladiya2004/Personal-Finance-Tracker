from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Category, Notification, Transaction


class UserDataIsolationTests(TestCase):
    """User B must never see or change user A's data."""

    def setUp(self):
        self.user_a = User.objects.create_user(username='alice', password='testpass123')
        self.user_b = User.objects.create_user(username='bob', password='testpass123')
        self.category_a = Category.objects.create(user=self.user_a, name='AliceCategory')
        self.transaction_a = Transaction.objects.create(
            user=self.user_a,
            title='Alice Rent',
            amount='700.00',
            transaction_type='expense',
            category=self.category_a,
            date=date(2026, 2, 1),
        )
        Notification.objects.create(user=self.user_a, title='Notice', message='AliceNotice')
        self.client.login(username='bob', password='testpass123')

    def test_edit_page_of_other_users_transaction_returns_404(self):
        response = self.client.get(
            reverse('expenses:edit_transaction', args=[self.transaction_a.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_edit_post_to_other_users_transaction_is_rejected_and_data_unchanged(self):
        response = self.client.post(
            reverse('expenses:edit_transaction', args=[self.transaction_a.id]),
            {
                'title': 'Hacked',
                'amount': '1.00',
                'transaction_type': 'income',
                'date': '2026-02-02',
                'category': self.category_a.id,
            },
        )

        self.transaction_a.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.transaction_a.title, 'Alice Rent')
        self.assertEqual(self.transaction_a.amount, Decimal('700.00'))

    def test_delete_of_other_users_transaction_does_nothing(self):
        response = self.client.post(
            reverse('expenses:delete_transaction', args=[self.transaction_a.id])
        )

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertTrue(Transaction.objects.filter(id=self.transaction_a.id).exists())

    def test_cannot_create_transaction_with_other_users_category(self):
        Category.objects.create(user=self.user_b, name='BobCategory')

        response = self.client.post(
            reverse('expenses:add_transaction'),
            {
                'title': 'Sneaky',
                'amount': '5.00',
                'transaction_type': 'expense',
                'category': self.category_a.id,
                'date': '2026-02-03',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.context['form'].errors)
        self.assertFalse(Transaction.objects.filter(title='Sneaky').exists())

    def test_transaction_list_hides_other_users_transactions(self):
        response = self.client.get(reverse('expenses:transaction_list'))

        self.assertNotContains(response, 'Alice Rent')

    def test_dashboard_totals_ignore_other_users_transactions(self):
        response = self.client.get(reverse('expenses:dashboard'))

        self.assertEqual(response.context['total_expenses'], 0)
        self.assertEqual(response.context['balance'], 0)
        self.assertNotContains(response, 'Alice Rent')

    def test_category_list_hides_other_users_categories(self):
        response = self.client.get(reverse('expenses:category_list'))

        self.assertNotContains(response, 'AliceCategory')

    def test_notifications_hide_other_users_notifications(self):
        response = self.client.get(reverse('expenses:notifications'))

        self.assertNotContains(response, 'AliceNotice')
