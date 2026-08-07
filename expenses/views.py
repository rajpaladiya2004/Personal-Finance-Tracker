from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.views.decorators.http import require_POST
from .forms import CategoryForm, RegisterForm, TransactionForm, UserProfileForm
from .models import Category, Notification, Transaction, UserProfile


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
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save()
            Notification.objects.create(
                user=request.user,
                title='New category added',
                message=f'Category: {category.name}',
            )
            messages.success(request, 'Category added successfully.')
            return redirect('expenses:add_category')
    else:
        form = CategoryForm(user=request.user)
    categories = Category.objects.filter(user=request.user).order_by('name')
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
def notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'expenses/notifications.html', {'notifications': page_obj})


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
def contact_us(request):
    return render(request, 'expenses/contact_us.html')


@login_required
def faq(request):
    return render(request, 'expenses/faq.html')


@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'expenses/category_list.html', {'categories': categories})


@login_required
def add_transaction(request):
    categories = Category.objects.filter(user=request.user).order_by('name')

    if not categories.exists():
        messages.warning(request, 'Please add a category first before creating a transaction.')
        return render(
            request,
            'expenses/add_transaction.html',
            {
                'form': None,
                'needs_category': True,
            },
        )

    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save()
            transaction_label = 'Income' if transaction.transaction_type == 'income' else 'Expense'
            Notification.objects.create(
                user=request.user,
                title=f'New {transaction_label.lower()} added',
                message=f'{transaction_label}: {transaction.title} - {transaction.amount}',
                transaction=transaction,
            )
            messages.success(request, 'Transaction added successfully.')
            return redirect('expenses:transaction_list')
    else:
        form = TransactionForm(user=request.user)
    return render(request, 'expenses/add_transaction.html', {'form': form, 'needs_category': False})


@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully.')
            return redirect('expenses:transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    return render(request, 'expenses/edit_transaction.html', {'form': form, 'transaction': transaction})


@login_required
@require_POST
def delete_transaction(request, transaction_id):
    transaction = Transaction.objects.filter(id=transaction_id, user=request.user).first()

    if transaction is None:
        messages.error(request, 'Transaction not found.')
        return redirect('expenses:transaction_list')

    transaction.delete()
    messages.success(request, 'Transaction deleted successfully.')
    return redirect('expenses:transaction_list')


@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    paginator = Paginator(transactions, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'expenses/transaction_list.html', {'transactions': page_obj})


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




