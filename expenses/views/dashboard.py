from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.shortcuts import render

from ..models import Transaction, UserProfile


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    total_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = total_income - total_expenses

    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-created_at')[:5]

    category_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')

    monthly_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense'
    ).annotate(month=TruncMonth('date')).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')

    yearly_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense'
    ).annotate(year=TruncYear('date')).values('year').annotate(
        total=Sum('amount')
    ).order_by('-year')

    context = {
        'profile': profile,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'category_expenses': category_expenses,
        'monthly_expenses': monthly_expenses,
        'yearly_expenses': yearly_expenses,
    }
    return render(request, 'expenses/dashboard.html', context)
