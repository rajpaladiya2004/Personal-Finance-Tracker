from django import forms

from ..models import Category, Transaction


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

    def clean_amount(self):
        amount = self.cleaned_data['amount']

        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')

        return amount

    def save(self, commit=True):
        transaction = super().save(commit=False)
        if self.user is not None:
            transaction.user = self.user
        if commit:
            transaction.save()
        return transaction
