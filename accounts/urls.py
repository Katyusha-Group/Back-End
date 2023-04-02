
from django.contrib import admin
from django.urls import path, include


app_name = 'accounts'

urlpatterns = [
    path('', include('accounts.api.urls')),

]
