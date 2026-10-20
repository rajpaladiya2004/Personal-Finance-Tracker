from django import forms

from ..models import Category


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']

        if self.user is not None and Category.objects.filter(user=self.user, name__iexact=name).exists():
            raise forms.ValidationError('You already have a category with this name.')

        return name

    def save(self, commit=True):
        category = super().save(commit=False)
        if self.user is not None:
            category.user = self.user
        if commit:
            category.save()
        return category
