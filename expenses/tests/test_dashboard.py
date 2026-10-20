from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from ..models import Category, Transaction, UserProfile


class DashboardRecentTransactionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='testpass123',
        )

    def test_dashboard_shows_only_latest_five_transactions(self):
        self.client.login(username='student', password='testpass123')

        start_date = date(2026, 1, 1)
        for index in range(6):
            Transaction.objects.create(
                user=self.user,
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

    def test_dashboard_shows_profile_info_section(self):
        UserProfile.objects.create(user=self.user, phone_number='1234567890')
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username:')
        self.assertContains(response, 'student@example.com')
        self.assertContains(response, '1234567890')


class DashboardTotalsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.food = Category.objects.create(user=self.user, name='Food')
        self.travel = Category.objects.create(user=self.user, name='Travel')
        self.client.login(username='student', password='testpass123')

    def add(self, amount, kind, category, when):
        return Transaction.objects.create(
            user=self.user,
            title=f'{kind} {amount}',
            amount=amount,
            transaction_type=kind,
            category=category,
            date=when,
        )

    def test_dashboard_with_no_transactions_shows_zero_totals(self):
        response = self.client.get(reverse('expenses:dashboard'))

        self.assertEqual(response.context['total_income'], 0)
        self.assertEqual(response.context['total_expenses'], 0)
        self.assertEqual(response.context['balance'], 0)

    def test_dashboard_totals_and_balance_are_correct(self):
        self.add('100.00', 'income', self.food, date(2026, 1, 5))
        self.add('50.00', 'income', self.food, date(2026, 1, 6))
        self.add('30.50', 'expense', self.food, date(2026, 1, 7))
        self.add('19.50', 'expense', self.travel, date(2026, 1, 8))

        response = self.client.get(reverse('expenses:dashboard'))

        self.assertEqual(response.context['total_income'], Decimal('150.00'))
        self.assertEqual(response.context['total_expenses'], Decimal('50.00'))
        self.assertEqual(response.context['balance'], Decimal('100.00'))

    def test_balance_is_negative_when_expenses_exceed_income(self):
        self.add('10.00', 'income', self.food, date(2026, 1, 5))
        self.add('25.00', 'expense', self.food, date(2026, 1, 6))

        response = self.client.get(reverse('expenses:dashboard'))

        self.assertEqual(response.context['balance'], Decimal('-15.00'))

    def test_category_expenses_are_grouped_and_exclude_income(self):
        self.add('30.50', 'expense', self.food, date(2026, 1, 7))
        self.add('10.00', 'expense', self.food, date(2026, 1, 8))
        self.add('19.50', 'expense', self.travel, date(2026, 1, 9))
        self.add('500.00', 'income', self.food, date(2026, 1, 10))

        response = self.client.get(reverse('expenses:dashboard'))

        rows = {row['category__name']: row['total'] for row in response.context['category_expenses']}
        self.assertEqual(rows, {'Food': Decimal('40.50'), 'Travel': Decimal('19.50')})

    def test_monthly_and_yearly_expenses_are_grouped(self):
        self.add('10.00', 'expense', self.food, date(2026, 1, 5))
        self.add('15.00', 'expense', self.food, date(2026, 1, 20))
        self.add('20.00', 'expense', self.food, date(2026, 2, 3))
        self.add('5.00', 'expense', self.food, date(2025, 12, 31))

        response = self.client.get(reverse('expenses:dashboard'))

        monthly = {row['month']: row['total'] for row in response.context['monthly_expenses']}
        yearly = {row['year'].year: row['total'] for row in response.context['yearly_expenses']}
        self.assertEqual(monthly[date(2026, 1, 1)], Decimal('25.00'))
        self.assertEqual(monthly[date(2026, 2, 1)], Decimal('20.00'))
        self.assertEqual(yearly, {2026: Decimal('45.00'), 2025: Decimal('5.00')})
