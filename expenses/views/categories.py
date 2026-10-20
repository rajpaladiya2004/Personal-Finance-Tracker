from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from ..forms import CategoryForm
from ..models import Category, Notification


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
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'expenses/category_list.html', {'categories': categories})
