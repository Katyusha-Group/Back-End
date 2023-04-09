
from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
      TokenObtainPairView,
      TokenRefreshView,
      TokenVerifyView
)




urlpatterns = [
      path('signup/', views.SignUpView.as_view(), name='signup'),
      path('login/', views.LoginView.as_view(), name='login'),
      path('logout/', views.LogoutView.as_view(), name='logout'),
      # path('change-password/', views.ActivationResend.as_view(), name='change-password'),
      # path('confirm-email/', views.ConfirmEmailView.as_view(), name='confirm-email'),
      path('activation-confirm/<str:token>/', views.ActivationConfirmView.as_view(), name='activation-confirm'),
      path('activation-resend/', views.ActivationResend.as_view(), name='activation-resend'),
      path('create/', views.CustomTokenObtainPairView.as_view(), name='create-token'),
      path('refresh/', TokenRefreshView.as_view(), name='refresh-token'),
      path('verify/', TokenVerifyView.as_view(), name='verify-token'),

]
