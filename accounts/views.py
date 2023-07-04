import random
from datetime import datetime, timedelta

from django.contrib.auth.hashers import make_password
from rest_framework import generics, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response

from utils import email_handler
from .serializers import *
from .serializers import LoginSerializer
from accounts.models import User
from django.conf import settings
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import status
from mail_templated import EmailMessage
from .signals import wallet_updated_signal
from .utils import EmailThread
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ActivationResendSerializer
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError


class SignUpView(APIView):
    serializer_class = SignUpSerializer

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # validate password
        try:
            validate_password(request.data['password1'])
        except exception.ValidationError as e:
            return Response({"password": e.messages}, status=400)
        email = serializer.validated_data['email']

        verification_code = str(random.randint(1000, 9999))

        # Save user
        user = User.objects.create(
            department=validated_data['department'],
            username=validated_data['email'],
            email=validated_data['email'],
            gender=validated_data['gender'],
            password=make_password(validated_data['password1']),
            verification_code=verification_code,
        )

        token = self.get_token_for_user(user)
        subject = 'تایید ایمیل ثبت نام'
        message = 'سلام! به کاتیوشا خوش آمدید.\n'
        message += 'با تشکر از ثبت‌نام شما در کاتیوشا، لطفاً برای تایید ایمیل خود و فعال‌سازی حساب کاربری‌تان، کد تایید زیر را در سایت وارد کنید:\n'
        message += f'{verification_code}\n'
        message += 'با تشکر،\n'
        message += 'تیم کاتیوشا'
        email_handler.send_verification_message(subject=subject,
                                                recipient_list=[user.email],
                                                verification_token=verification_code)

        return Response({
            "user": {"department": user.department.name, "email": email,
                     "gender": user.gender},
            "message": "User created successfully. Please check your email to activate your account. ",
            "code": verification_code,
            "url": f'http://katyushaiust.ir/accounts/activation-confirm/{token}',
            "token": token,
        }, status=201)

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # token, created = Token.objects.get_or_create(user=user)
        token = self.generate_jwt_token(user.id)
        login(request, user)
        return Response({'token': token,
                         'user_id': user.id,
                         'username': user.username,
                         'email': user.email,
                         })

    @staticmethod
    def generate_jwt_token(user_id):
        # Define the expiration time of the token
        exp_time = datetime.utcnow() + timedelta(days=7)

        # Define the payload of the token
        # payload = {
        #     'user_id': user_id,
        #     'exp': exp_time
        # }

        # Generate the token using the JWT package and your Django SECRET_KEY setting
        # token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        refresh = RefreshToken.for_user(User.objects.get(id=user_id))
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        # Return the token as a string
        return token


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # permission_classes = []

    def get(self, request):
        refresh_token = request.COOKIES.get('token')
        if refresh_token:
            token = Token.objects.get(refresh_token=refresh_token)
            token.blacklist()
            response = Response()
            response.delete_cookie('refresh_token')
            response.delete_cookie('access_token')
            return response(data={'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
        else:
            if request.user.is_authenticated:
                logout(request)
                return Response(data={'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)
            else:
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
        self.is_valid_token(token)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user_from_token(token)

        if request.data.get('verification_code') != user.verification_code:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        user_obj = get_object_or_404(User, email=user.email)
        user_obj.is_email_verified = True
        user.verification_code = None
        user.delete()
        user_obj.save()

        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)

    @staticmethod
    def get_user_from_token(token):
        # decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # get the user
        user = User.objects.filter(id=payload['user_id']).first()
        return user

    @staticmethod
    def is_valid_token(token):
        try:
            # Decode the token with the secret key
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            # If decoding is successful, the token is valid
            return True
        except ExpiredSignatureError:
            # If the token has expired, it is invalid
            return False
        except InvalidSignatureError:
            # If the signature is invalid, the token is invalid
            return False

    def get(self, request, token):
        try:
            decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except:
            return Response({'message': 'Invalid URL'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Please enter code verification'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ActivationResend(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.validated_data['user']
            token = self.get_token_for_user(user_obj)
            email_obj = EmailMessage('email/activation_email.tpl', {'token': token}, 'asad@asd.com',
                                     to=[user_obj.email])
            EmailThread(email_obj).start()
            return Response({"message": "email sent"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


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
        if request.method == 'GET':
            wallet = WalletSerializer(
                Wallet.objects.filter(user=self.request.user).first(),
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
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=404)

        if user.count_of_verification_code_sent >= 3:
            return Response({
                'detail': 'You have made more than 3 attempts to recover your forgotten password.Please contact support.'},
                status=429)

        verification_code = str(random.randint(1000, 9999))

        token = self.get_token_for_user(user)

        user.verification_code = verification_code
        user.count_of_verification_code_sent = user.count_of_verification_code_sent + 1
        user.save()

        subject = 'بازیابی رمز عبور'
        email_handler.send_forget_password_verification_message(subject=subject,
                                                                verification_token=verification_code,
                                                                recipient_list=[user.email])

        return Response({'detail': 'Code Sent',
                         'link': f'http://katyushaiust.ir/accounts/code_verification_view/{token}/'
                         })

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


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
            return Response({'detail': 'URL is not valid.'})

        serializer = CodeVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user_from_token(token)

        if request.data.get('verification_code') != user.verification_code:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        user_obj = get_object_or_404(User, email=user.email)
        user.verification_code = None
        user.delete()
        user_obj.save()

        return Response(
            {'message': 'code is valid', 'link': f'http://katyushaiust.ir/accounts/change-password/{token}/'},
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


class ProfileViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch', 'head', 'options']
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'delete':
            return [IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_object(self):
        return get_object_or_404(self.get_queryset(), user=self.request.user)

    def perform_create(self, serializer):
        print(serializer.validated_data)
        serializer.save(user=self.request.user)
