from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import TransactionForm
from ..models import Category, Notification, Transaction


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
                message=f'{transaction_label}: {transaction.title} - €{transaction.amount}',
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
