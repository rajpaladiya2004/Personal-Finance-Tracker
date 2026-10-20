from django import forms

from ..models import UserProfile


class UserProfileForm(forms.ModelForm):
    phone_number = forms.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ['phone_number']
