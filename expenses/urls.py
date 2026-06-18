from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/', views.category_list, name='category_list'),
    path('transaction/add/', views.add_transaction, name='add_transaction'),
    path('transaction/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transaction/', views.transaction_list, name='transaction_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
