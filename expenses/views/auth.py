from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import RegisterForm
from ..models import UserProfile


def home(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')
    return render(request, 'expenses/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('expenses:login')
        messages.error(request, 'Please correct the registration errors below.')
    else:
        form = RegisterForm()
    return render(request, 'expenses/register.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        UserProfile.objects.filter(user=user).delete()
        user.delete()
        logout(request)
        return redirect('expenses:login')

    return render(request, 'expenses/delete_account_confirm.html')
