from django.urls import path, include
from accounts import views
from rest_framework_nested import routers
from rest_framework_simplejwt.views import (
      TokenRefreshView,
      TokenVerifyView
)

router = routers.DefaultRouter()
router.register(r'wallet', viewset=views.WalletViewSet, basename='wallet')


urlpatterns = [
      path('', include(router.urls)),
      path('signup/', views.SignUpView.as_view(), name='signup'),
      path('login/', views.LoginView.as_view(), name='login'),
      path('logout/', views.LogoutView.as_view(), name='logout'),
      path('change-password/', views.ActivationResend.as_view(), name='change-password'),
      path('activation-confirm/<str:token>/', views.ActivationConfirmView.as_view(), name='activation-confirm'),
      path('activation-resend/', views.ActivationResend.as_view(), name='activation-resend'),
      path('create/', views.CustomTokenObtainPairView.as_view(), name='create-token'),
      path('refresh/', TokenRefreshView.as_view(), name='refresh-token'),
      path('verify/', TokenVerifyView.as_view(), name='verify-token'),
      path('reset-password/', views.ForgotPasswordView.as_view()),
      path('change-password/<str:token>/', views.PasswordChangeAPIView.as_view()),
      path('code_verification_view/<str:token>/', views.CodeVerificationView.as_view()),
      path('changepassword/', views.ChangePasswordlogView.as_view()),
]
