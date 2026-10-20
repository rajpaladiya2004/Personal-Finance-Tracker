from datetime import date

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import Category, Notification, Transaction


class AddTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.category = Category.objects.create(user=self.user, name='Food')
        self.client.login(username='student', password='testpass123')
        self.url = reverse('expenses:add_transaction')

    def valid_data(self, **overrides):
        data = {
            'title': 'Lunch',
            'amount': '12.50',
            'transaction_type': 'expense',
            'category': self.category.id,
            'description': 'Canteen',
            'date': '2026-03-10',
        }
        data.update(overrides)
        return data

    def test_add_transaction_creates_record_and_redirects(self):
        response = self.client.post(self.url, self.valid_data())

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        transaction = Transaction.objects.get(title='Lunch')
        self.assertEqual(transaction.user, self.user)
        self.assertEqual(str(transaction.amount), '12.50')
        self.assertEqual(transaction.transaction_type, 'expense')

    def test_add_transaction_creates_notification(self):
        self.client.post(self.url, self.valid_data())

        transaction = Transaction.objects.get(title='Lunch')
        self.assertTrue(
            Notification.objects.filter(user=self.user, transaction=transaction).exists()
        )

    def test_add_transaction_rejects_zero_amount(self):
        response = self.client.post(self.url, self.valid_data(amount='0'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('amount', response.context['form'].errors)
        self.assertFalse(Transaction.objects.exists())

    def test_add_transaction_rejects_negative_amount(self):
        response = self.client.post(self.url, self.valid_data(amount='-5.00'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('amount', response.context['form'].errors)
        self.assertFalse(Transaction.objects.exists())

    def test_add_transaction_rejects_non_numeric_amount(self):
        response = self.client.post(self.url, self.valid_data(amount='abc'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('amount', response.context['form'].errors)
        self.assertFalse(Transaction.objects.exists())

    def test_add_transaction_requires_category(self):
        response = self.client.post(self.url, self.valid_data(category=''))

        self.assertEqual(response.status_code, 200)
        self.assertIn('category', response.context['form'].errors)
        self.assertFalse(Transaction.objects.exists())

    def test_add_transaction_requires_title_and_date(self):
        response = self.client.post(self.url, self.valid_data(title='', date=''))

        self.assertEqual(response.status_code, 200)
        self.assertIn('title', response.context['form'].errors)
        self.assertIn('date', response.context['form'].errors)

    def test_add_transaction_without_categories_asks_user_to_add_one(self):
        Category.objects.all().delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['needs_category'])
        self.assertIsNone(response.context['form'])
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(
            str(messages[0]),
            'Please add a category first before creating a transaction.',
        )


class TransactionListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.client.login(username='student', password='testpass123')

    def test_transaction_list_is_paginated_by_ten(self):
        for index in range(12):
            Transaction.objects.create(
                user=self.user,
                title=f'Item {index}',
                amount='1.00',
                transaction_type='expense',
                date=date(2026, 1, index + 1),
            )

        first_page = self.client.get(reverse('expenses:transaction_list'))
        second_page = self.client.get(reverse('expenses:transaction_list') + '?page=2')

        self.assertEqual(len(first_page.context['transactions']), 10)
        self.assertEqual(len(second_page.context['transactions']), 2)

    def test_transaction_list_orders_newest_first(self):
        for day in (1, 3, 2):
            Transaction.objects.create(
                user=self.user,
                title=f'Day {day}',
                amount='1.00',
                transaction_type='expense',
                date=date(2026, 1, day),
            )

        response = self.client.get(reverse('expenses:transaction_list'))

        titles = [t.title for t in response.context['transactions']]
        self.assertEqual(titles, ['Day 3', 'Day 2', 'Day 1'])


class EditTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )
        self.category = Category.objects.create(user=self.user, name='Food')
        self.transaction = Transaction.objects.create(
            user=self.user,
            title='Groceries',
            amount='25.50',
            transaction_type='expense',
            category=self.category,
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
                'category': self.category.id,
            },
        )

        self.transaction.refresh_from_db()

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertEqual(self.transaction.title, 'Updated Groceries')
        self.assertEqual(str(self.transaction.amount), '30.00')
        self.assertEqual(self.transaction.description, 'Updated shopping')

    def test_edit_transaction_rejects_invalid_amount_and_keeps_data(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:edit_transaction', args=[self.transaction.id]),
            {
                'title': 'Groceries',
                'amount': '-1',
                'transaction_type': 'expense',
                'description': 'Weekly shopping',
                'date': '2026-03-10',
                'category': self.category.id,
            },
        )

        self.transaction.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIn('amount', response.context['form'].errors)
        self.assertEqual(str(self.transaction.amount), '25.50')


class DeleteTransactionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='student',
            password='testpass123',
        )
        self.transaction = Transaction.objects.create(
            user=self.user,
            title='Bus Ticket',
            amount='5.00',
            transaction_type='expense',
            description='Travel cost',
            date=date(2026, 4, 1),
        )

    def test_delete_transaction_removes_item_and_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:delete_transaction', args=[self.transaction.id])
        )

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertFalse(
            Transaction.objects.filter(id=self.transaction.id).exists()
        )

    def test_delete_transaction_rejects_get_requests(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(
            reverse('expenses:delete_transaction', args=[self.transaction.id])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Transaction.objects.filter(id=self.transaction.id).exists())

    def test_transaction_list_shows_delete_link(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.get(reverse('expenses:transaction_list'))

        self.assertContains(
            response,
            reverse('expenses:delete_transaction', args=[self.transaction.id]),
        )

    def test_delete_non_existing_transaction_shows_error_and_redirects(self):
        self.client.login(username='student', password='testpass123')

        response = self.client.post(
            reverse('expenses:delete_transaction', args=[9999])
        )

        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, reverse('expenses:transaction_list'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Transaction not found.')
        self.assertEqual(messages[0].tags, 'error')
