from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Category, Transaction, UserProfile


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        category = super().save(commit=False)
        if self.user is not None:
            category.user = self.user
        if commit:
            category.save()
        return category


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['title', 'amount', 'transaction_type', 'category', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['category'].required = True
        if self.user is not None:
            self.fields['category'].queryset = Category.objects.filter(user=self.user).order_by('name')
        else:
            self.fields['category'].queryset = Category.objects.none()

    def save(self, commit=True):
        transaction = super().save(commit=False)
        if self.user is not None:
            transaction.user = self.user
        if commit:
            transaction.save()
        return transaction


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')

        return email


class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone_number']
