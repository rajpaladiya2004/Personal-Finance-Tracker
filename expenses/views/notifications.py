from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render

from ..models import Notification


@login_required
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'expenses/notifications.html', {'notifications': page_obj})
