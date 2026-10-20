from django.urls import path

from .. import views

urlpatterns = [
    path('notifications/', views.notifications, name='notifications'),
    path('help-support/', views.help_support, name='help_support'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('about-us/', views.about_us, name='about_us'),
    path('contact-us/', views.contact_us, name='contact_us'),
    path('faq/', views.faq, name='faq'),
]
