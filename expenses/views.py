from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from .forms import CategoryForm, TransactionForm
from .models import Category, Transaction


def home(request):
    if request.user.is_authenticated:
        return redirect('expenses:dashboard')
    return render(request, 'expenses/home.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('expenses:login')
    else:
        form = UserCreationForm()
    return render(request, 'expenses/register.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('expenses:home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('expenses:home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'expenses/login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('expenses:login')


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('expenses:add_category')
    else:
        form = CategoryForm()
    categories = Category.objects.all().order_by('name')
    return render(request, 'expenses/add_category.html', {'form': form, 'categories': categories})


@login_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'expenses/category_list.html', {'categories': categories})


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction added successfully.')
            return redirect('expenses:transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'expenses/add_transaction.html', {'form': form})


@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'expenses/transaction_list.html', {'transactions': transactions})


@login_required
def dashboard(request):
    total_income = Transaction.objects.filter(
        transaction_type='income'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_expenses = Transaction.objects.filter(
        transaction_type='expense'
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = total_income - total_expenses

    recent_transactions = Transaction.objects.all().order_by('-date', '-created_at')[:5]

    category_expenses = Transaction.objects.filter(
        transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')

    monthly_expenses = Transaction.objects.filter(
        transaction_type='expense'
    ).annotate(month=TruncMonth('date')).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')

    yearly_expenses = Transaction.objects.filter(
        transaction_type='expense'
    ).annotate(year=TruncYear('date')).values('year').annotate(
        total=Sum('amount')
    ).order_by('-year')

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'category_expenses': category_expenses,
        'monthly_expenses': monthly_expenses,
        'yearly_expenses': yearly_expenses,
    }
    return render(request, 'expenses/dashboard.html', context)
