from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='expenses/login.html',
            next_page='expenses:dashboard',
            redirect_authenticated_user=True,
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='expenses:login'),
        name='logout',
    ),
    path(
        'change-password/',
        auth_views.PasswordChangeView.as_view(
            template_name='expenses/change_password.html',
            success_url='/change-password/success/',
        ),
        name='change_password',
    ),
    path(
        'change-password/success/',
        TemplateView.as_view(
            template_name='expenses/change_password_done.html',
        ),
        name='change_password_done',
    ),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('delete-account/confirm/', views.delete_account, name='delete_account_confirm'),
    path('order-history/', views.order_history, name='order_history'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('profile/', views.profile, name='profile'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/', views.category_list, name='category_list'),
    path('transaction/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transaction/edit/<int:transaction_id>/', views.edit_transaction),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('transaction/', views.transaction_list, name='transaction_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]


