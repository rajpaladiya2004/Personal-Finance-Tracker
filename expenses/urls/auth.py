from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from .. import views

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
    path('profile/', views.profile, name='profile'),
]
