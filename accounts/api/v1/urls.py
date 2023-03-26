
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
      path('signup/', views.SignUpView.as_view(), name='signup'),
      path('login/', views.LoginView.as_view(), name='login'),
      path('logout/', views.LogoutView.as_view(), name='logout'),
      path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
      # path('confirm-email/', views.ConfirmEmailView.as_view(), name='confirm-email'),
      path('test/', views.TestView.as_view(), name='test'),
    
]
