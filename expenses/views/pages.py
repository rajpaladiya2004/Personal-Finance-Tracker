from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import ContactMessageForm


@login_required
def help_support(request):
    return render(request, 'expenses/help_support.html')


@login_required
def terms_conditions(request):
    return render(request, 'expenses/terms_conditions.html')


@login_required
def privacy_policy(request):
    return render(request, 'expenses/privacy_policy.html')


@login_required
def about_us(request):
    return render(request, 'expenses/about_us.html')


@login_required
def faq(request):
    return render(request, 'expenses/faq.html')


@login_required
def contact_us(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will get back to you soon.')
            return redirect('expenses:contact_us')
        messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactMessageForm()
    return render(request, 'expenses/contact_us.html', {'form': form})
