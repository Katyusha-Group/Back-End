
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
      path('signup/', views.SignUpView.as_view(), name='signup'),
      path('login/', views.LoginView.as_view(), name='login'),
      path('logout/', views.LogoutView.as_view(), name='logout'),
    
]
