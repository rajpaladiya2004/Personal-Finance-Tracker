from django.urls import include, path

app_name = 'expenses'

urlpatterns = [
    path('', include('expenses.urls.auth')),
    path('', include('expenses.urls.transactions')),
    path('', include('expenses.urls.pages')),
]
