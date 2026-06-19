from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from .forms import CategoryForm, RegisterForm, TransactionForm, UserProfileForm
from .models import Category, Transaction, UserProfile


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


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        UserProfile.objects.filter(user=user).delete()
        user.delete()
        logout(request)
        return redirect('expenses:login')

    return render(request, 'expenses/delete_account_confirm.html')


@login_required
def order_history(request):
    return render(request, 'expenses/order_history.html')


@login_required
def wishlist(request):
    return render(request, 'expenses/wishlist.html')


@login_required
def profile_settings(request):
    return render(request, 'expenses/profile_settings.html')


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
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully.')
            return redirect('expenses:transaction_list')
    else:
        form = TransactionForm(instance=transaction)

    return render(request, 'expenses/edit_transaction.html', {'form': form, 'transaction': transaction})


@login_required
def delete_transaction(request, transaction_id):
    transaction = Transaction.objects.filter(id=transaction_id).first()

    if transaction is None:
        messages.error(request, 'Transaction not found.')
        return redirect('expenses:transaction_list')

    transaction.delete()
    messages.success(request, 'Transaction deleted successfully.')
    return redirect('expenses:transaction_list')


@login_required
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-date')
    return render(request, 'expenses/transaction_list.html', {'transactions': transactions})


@login_required
def dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

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



