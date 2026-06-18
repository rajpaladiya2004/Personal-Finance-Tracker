from datetime import date, timedelta

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve
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


class AuthenticationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )

    def test_login_uses_built_in_view_and_redirects_to_dashboard(self):
        response = self.client.post(
            reverse('expenses:login'),
            {
                'username': 'student',
                'password': 'testpass123',
            },
        )

        self.assertRedirects(response, reverse('expenses:dashboard'))

    def test_logout_redirects_to_login_page(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:logout'))

        self.assertRedirects(response, reverse('expenses:login'))


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


class EditTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )
        self.transaction = Transaction.objects.create(
            title='Groceries',
            amount='25.50',
            transaction_type='expense',
            description='Weekly shopping',
            date=date(2026, 3, 10),
        )

    def test_edit_transaction_prefills_existing_data(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(
            reverse('expenses:edit_transaction', args=[self.transaction.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Groceries')
        self.assertContains(response, 'Weekly shopping')

    def test_edit_transaction_url_uses_plural_transactions_path(self):
        edit_url = reverse('expenses:edit_transaction', args=[self.transaction.id])

        self.assertEqual(edit_url, f'/transactions/edit/{self.transaction.id}/')
        self.assertEqual(resolve(edit_url).func.__name__, 'edit_transaction')

    def test_edit_transaction_updates_and_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:edit_transaction', args=[self.transaction.id]),
            {
                'title': 'Updated Groceries',
                'amount': '30.00',
                'transaction_type': 'expense',
                'description': 'Updated shopping',
                'date': '2026-03-12',
                'category': '',
            },
        )

        self.transaction.refresh_from_db()

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertEqual(self.transaction.title, 'Updated Groceries')
        self.assertEqual(str(self.transaction.amount), '30.00')
        self.assertEqual(self.transaction.description, 'Updated shopping')


class DeleteTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )
        self.transaction = Transaction.objects.create(
            title='Bus Ticket',
            amount='5.00',
            transaction_type='expense',
            description='Travel cost',
            date=date(2026, 4, 1),
        )

    def test_delete_transaction_removes_item_and_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(
            reverse('expenses:delete_transaction', args=[self.transaction.id])
        )

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertFalse(
            Transaction.objects.filter(id=self.transaction.id).exists()
        )

    def test_transaction_list_shows_delete_link(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:transaction_list'))

        self.assertContains(
            response,
            reverse('expenses:delete_transaction', args=[self.transaction.id]),
        )

    def test_delete_non_existing_transaction_shows_error_and_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(
            reverse('expenses:delete_transaction', args=[9999])
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Transaction not found.')
        self.assertEqual(messages[0].tags, 'error')
