from django.urls import path

from .. import views

urlpatterns = [
    path('category/add/', views.add_category, name='add_category'),
    path('category/', views.category_list, name='category_list'),
    path('transaction/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('transaction/', views.transaction_list, name='transaction_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
