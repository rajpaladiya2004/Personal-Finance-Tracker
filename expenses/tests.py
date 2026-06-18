from datetime import date, timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Transaction


class DashboardRecentTransactionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )

    def test_dashboard_shows_only_latest_five_transactions(self):
        self.client.login(username='student', password='testpass123')

        start_date = date(2026, 1, 1)
        for index in range(6):
            Transaction.objects.create(
                title=f'Transaction {index + 1}',
                amount='10.00',
                transaction_type='expense',
                date=start_date + timedelta(days=index),
            )

        response = self.client.get(reverse('expenses:dashboard'))

        recent_transactions = list(response.context['recent_transactions'])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(recent_transactions), 5)
        self.assertEqual(recent_transactions[0].title, 'Transaction 6')
        self.assertEqual(recent_transactions[-1].title, 'Transaction 2')
        self.assertContains(response, 'Transaction 6')
        self.assertNotContains(response, 'Transaction 1')
