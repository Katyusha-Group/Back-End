import random
from datetime import datetime

from django.contrib.auth.hashers import make_password
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from social_media.models import Profile
from utils.email import email_handler
from utils.variables import project_variables
from .serializers import LoginSerializer, SignUpSerializer, UserSerializer, ChangePasswordSerializer, \
    ActivationConfirmSerializer, CustomTokenObtainPairSerializer, WalletSerializer, ModifyWalletSerializer, \
    WalletTransactionSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, CodeVerificationSerializer
from accounts.models import User, Wallet, WalletTransaction
from django.conf import settings
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .signals import wallet_updated_signal
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ActivationResendSerializer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from .utils import EmailThread, generate_tokens
from rest_framework.permissions import IsAdminUser
from django.utils import timezone
from datetime import timedelta
from django.db import models


class SignUpView(GenericAPIView):
    serializer_class = SignUpSerializer

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        email = str.lower(validated_data['email'])

        verification_code = str(random.randint(1000, 9999))
        user = User.objects.filter(email__iexact=email)

        # if user signup before and not verified
        if user.exists():
            user = user.first()
            user.department = validated_data['department']
            user.gender = validated_data['gender']
            user.password = make_password(validated_data['password1'])
            user.verification_code = verification_code
            user.verification_tries_count += 1
            user.last_verification_sent = datetime.now()
            user.save()
        else:
            # if user didnt signup before
            user = User.objects.create(
                department=validated_data['department'],
                username=validated_data['username'],
                email=email,
                gender=validated_data['gender'],
                password=make_password(validated_data['password1']),
                verification_code=verification_code,
                verification_tries_count=1,
                last_verification_sent=datetime.now(),
            )

        # Saving profile
        profile = Profile.get_profile_for_user(user=user)
        profile.name = validated_data['name']

        # utils.get_access_token_for_user(user)
        token = generate_tokens(user.id)["access"]

        subject = 'تایید ایمیل ثبت نام'
        show_text = user.has_verification_tries_reset or user.verification_tries_count > 1

        # sending email verification with thread
        email_thread = EmailThread(email_handler, subject=subject,
                                   recipient_list=[user.email],
                                   verification_token=verification_code,
                                   registration_tries=user.verification_tries_count,
                                   show_text=show_text)
        email_thread.start()

        user_data = {
            "user": UserSerializer(user).data,
            "message": "User created successfully. Please check your email to activate your account.",
            "code": verification_code,
            "url": f'{settings.WEBSITE_URL}/accounts/activation-confirm/{token}',
            "token": token,

        }

        return Response(user_data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user is not None:
            tokens = generate_tokens(user.id)

            login(request, user)

            return Response({
                'refresh': tokens['refresh'],
                'access': tokens['access'],
                'user': UserSerializer(user).data,
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        refresh_token = request.COOKIES.get('token')

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                return Response(data={'detail': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            response = Response(data={'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response

        if request.user.is_authenticated:
            logout(request)
            return Response(data={'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)

        return Response(data={'detail': 'Not logged in, so cannot log out'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response({"status": "password set"}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivationConfirmView(GenericAPIView):
    serializer_class = ActivationConfirmSerializer
    permission_classes = []

    def post(self, request, token):
        token = self.validate_token(token)
        if not token:
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_user_from_token(token)
        if not user:
            return Response({'message': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('verification_code') != user.verification_code:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_email_verified = True
        user.verification_code = None
        user.save()

        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)

    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            return User.objects.filter(id=user_id).first()
        except ExpiredSignatureError:
            return None

    def validate_token(self, token):
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            return token
        except ExpiredSignatureError:
            return None
        except InvalidSignatureError:
            return None


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ActivationResend(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            subject = 'تایید ایمیل ثبت نام'
            verification_code = str(random.randint(1000, 9999))
            user.verification_tries_count += 1
            user.verification_code = verification_code
            user.last_verification_sent = datetime.now()
            user.save()
            show_text = user.has_verification_tries_reset or user.verification_tries_count > 1
            token = generate_tokens(user)["access"]
            email_handler.send_verification_message(subject=subject,
                                                    recipient_list=[user.email],
                                                    verification_token=verification_code,
                                                    registration_tries=user.verification_tries_count,
                                                    show_text=show_text)
            return Response({
                "message": "email sent",
                "url": f'{settings.WEBSITE_URL}/accounts/activation-confirm/{token}',
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletViewSet(viewsets.GenericViewSet, ListModelMixin):
    http_method_names = ['get', 'put', 'options', 'head']
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        if self.action == 'me' and self.request.method == 'GET':
            return Wallet.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def see_wallet(self, request):
        user = self.request.user
        wallet = WalletSerializer(
            Wallet.objects.filter(user=user).first(),
            context=self.get_serializer_context()
        )
        return Response(status=status.HTTP_200_OK, data=wallet.data)

    @action(detail=False, methods=['PUT'])
    def update_wallet(self, request):
        serializer = ModifyWalletSerializer(data=request.data, context={'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        wallet = serializer.update(self.request.user.wallet, serializer.validated_data)
        wallet_updated_signal.send_robust(sender=Wallet, wallet=wallet, amount=serializer.data['amount'])
        return Response(status=status.HTTP_200_OK, data=WalletSerializer(wallet).data)

    @action(detail=False, methods=['GET'])
    def transactions(self, request):
        transactions = WalletTransaction.objects.filter(user=self.request.user)
        serializer = WalletTransactionSerializer(transactions, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        if user.verification_tries_count >= project_variables.MAX_VERIFICATION_TRIES:
            return Response({
                'detail': f'You have made more than {project_variables.MAX_VERIFICATION_TRIES}'
                          f' attempts to recover your forgotten password.Please contact support.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS)

        verification_code = str(random.randint(1000, 9999))

        # utils.get_access_token_for_user(user)
        token = generate_tokens(user_id=user.id)["access"]

        user.verification_code = verification_code
        user.verification_tries_count = user.verification_tries_count + 1
        user.last_verification_sent = datetime.now()
        user.save()

        subject = 'بازیابی رمز عبور'
        email_handler.send_forget_password_verification_message(subject=subject,
                                                                verification_token=verification_code,
                                                                recipient_list=[user.email],
                                                                verification_tries=user.verification_tries_count)

        return Response(
            {
                'detail': 'Code Sent',
                'link': f'{settings.WEBSITE_URL}/accounts/code_verification_view/{token}/'
            }
        )


class PasswordChangeAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = ResetPasswordSerializer

    def post(self, request, token):
        serializer = ResetPasswordSerializer(data=request.data)
        try:
            self.is_valid_token(token)
        except:
            return Response({'detail': 'URL is not valid.'})

        user = self.get_user_from_token(token)

        if serializer.is_valid():
            # user = request.user
            password_1 = serializer.validated_data['new_password']

            user.set_password(password_1)
            user.save()

            return Response({'detail': 'Password successfully changed.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def is_valid_token(token):

        # Decode the token with the secret key
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

    @staticmethod
    def get_user_from_token(token):
        # decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # get the user
        user = User.objects.filter(id=payload['user_id']).first()
        return user


class CodeVerificationView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = CodeVerificationSerializer

    def post(self, request, token):
        try:
            self.is_valid_token(token)
        except:
            return Response({'detail': 'You have to put token inside the url.'})

        serializer = CodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user_from_token(token)

        if request.data.get('verification_code') != user.verification_code:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        user.verification_code = None
        user.save()

        return Response(
            {'message': 'code is valid', 'link': f'{settings.WEBSITE_URL}/accounts/change-password/{token}/'},
            status=status.HTTP_200_OK)

    @staticmethod
    def get_user_from_token(token):
        # decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # get the user
        user = User.objects.filter(id=payload['user_id']).first()
        return user

    @staticmethod
    def is_valid_token(token):

        # Decode the token with the secret key
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

    # def get(self, request, token):
    #     try:
    #         decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    #     except:
    #         return Response({'message': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({'message': 'Please enter code verification'}, status=status.HTTP_200_OK)
    #


class ChangePasswordlogView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Check if the current password matches the user's actual password
            if not user.check_password(old_password):
                return Response({'error': 'Invalid current password.'}, status=status.HTTP_400_BAD_REQUEST)

            # Change the user's password
            user.set_password(new_password)
            user.save()

            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserChartViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'head', 'options']
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()

    def get_serializer_class(self):
        return UserSerializer

    def last_week_users(self, request):
        # Calculate the date a week ago from the current date
        one_week_ago = timezone.now() - timedelta(days=6)

        # Query to get the users created in the last week
        users_created_last_week = User.objects.filter(
            date_joined__gte=one_week_ago  # Filter users created after one week ago
        ).extra({
            'created_date': "date(date_joined)"  # Extract date from the date_joined field
        }).values('created_date').annotate(
            users_count_per_day=models.Count('id')  # Count users per day
        ).order_by('created_date')

        # Create a dictionary mapping dates to the number of users created that day
        users_per_day_last_week_dict = {}
        for entry in users_created_last_week:
            users_per_day_last_week_dict[entry['created_date']] = entry['users_count_per_day']

        # Create a list of dates and number of users created that day
        users_per_day_last_week_list = []
        current_date = one_week_ago.date()
        while current_date <= timezone.now().date():
            users_per_day_last_week_list.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'users_count': users_per_day_last_week_dict.get(current_date, 0)
            })
            current_date += timedelta(days=1)

        # Return the response
        return Response(users_per_day_last_week_list, status=status.HTTP_200_OK)


class CheckIsAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({'is_admin': user.is_staff}, status=status.HTTP_200_OK)

class MakeAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_staff = True
        user.save()
        return Response({'message': 'User is now admin'}, status=status.HTTP_200_OK)
    
class MakeNormalView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_staff = False
        user.save()
        return Response({'message': 'User is now normal'}, status=status.HTTP_200_OK)