from django.contrib.auth.models import User
from django.test import TestCase

from ..forms import (
    CategoryForm,
    ContactMessageForm,
    RegisterForm,
    TransactionForm,
    UserProfileForm,
)
from ..models import Category


class RegisterFormTests(TestCase):
    def data(self, **overrides):
        data = {
            'username': 'newstudent',
            'email': 'new@example.com',
            'password1': 'testpass12345',
            'password2': 'testpass12345',
        }
        data.update(overrides)
        return data

    def test_valid_data_is_accepted(self):
        self.assertTrue(RegisterForm(self.data()).is_valid())

    def test_duplicate_email_is_rejected(self):
        User.objects.create_user(username='old', email='new@example.com', password='x')

        form = RegisterForm(self.data())

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_mismatched_passwords_are_rejected(self):
        form = RegisterForm(self.data(password2='different12345'))

        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_invalid_email_is_rejected(self):
        form = RegisterForm(self.data(email='not-an-email'))

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class TransactionFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        self.other = User.objects.create_user(username='other', password='testpass123')
        self.category = Category.objects.create(user=self.user, name='Food')
        self.other_category = Category.objects.create(user=self.other, name='Other')

    def data(self, **overrides):
        data = {
            'title': 'Lunch',
            'amount': '10.00',
            'transaction_type': 'expense',
            'category': self.category.id,
            'date': '2026-03-10',
        }
        data.update(overrides)
        return data

    def test_valid_data_is_accepted(self):
        self.assertTrue(TransactionForm(self.data(), user=self.user).is_valid())

    def test_zero_and_negative_amounts_are_rejected(self):
        for amount in ('0', '0.00', '-1'):
            with self.subTest(amount=amount):
                form = TransactionForm(self.data(amount=amount), user=self.user)
                self.assertFalse(form.is_valid())
                self.assertIn('amount', form.errors)

    def test_invalid_transaction_type_is_rejected(self):
        form = TransactionForm(self.data(transaction_type='gift'), user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('transaction_type', form.errors)

    def test_category_choices_are_limited_to_the_users_categories(self):
        form = TransactionForm(user=self.user)

        self.assertEqual(list(form.fields['category'].queryset), [self.category])

    def test_without_user_no_categories_are_available(self):
        form = TransactionForm()

        self.assertFalse(form.fields['category'].queryset.exists())

    def test_save_assigns_the_user(self):
        form = TransactionForm(self.data(), user=self.user)
        self.assertTrue(form.is_valid())

        self.assertEqual(form.save().user, self.user)


class CategoryFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='testpass123')
        Category.objects.create(user=self.user, name='Food')

    def test_duplicate_name_is_rejected_ignoring_case(self):
        form = CategoryForm({'name': 'FOOD'}, user=self.user)

        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_new_name_is_accepted_and_saved_for_user(self):
        form = CategoryForm({'name': 'Travel'}, user=self.user)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().user, self.user)


class UserProfileFormTests(TestCase):
    def test_phone_number_is_required(self):
        form = UserProfileForm({'phone_number': ''})

        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)

    def test_phone_number_is_accepted(self):
        self.assertTrue(UserProfileForm({'phone_number': '123456'}).is_valid())


class ContactMessageFormTests(TestCase):
    def test_all_fields_are_required(self):
        form = ContactMessageForm({})

        self.assertFalse(form.is_valid())
        for field in ('name', 'email', 'subject', 'message'):
            self.assertIn(field, form.errors)

    def test_save_assigns_the_user(self):
        user = User.objects.create_user(username='student', password='testpass123')
        form = ContactMessageForm(
            {'name': 'S', 'email': 's@example.com', 'subject': 'Hi', 'message': 'Hello'},
            user=user,
        )
        self.assertTrue(form.is_valid())

        self.assertEqual(form.save().user, user)
