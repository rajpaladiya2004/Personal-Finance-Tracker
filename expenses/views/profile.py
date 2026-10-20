from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import UserProfileForm
from ..models import UserProfile


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('expenses:profile')
        messages.error(request, 'Please correct the profile errors below.')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'expenses/profile.html', {'form': form, 'profile': profile})
