from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from .serializers import LoginSerializer
from accounts.models import User, Verification
from django.contrib.sites.shortcuts import get_current_site  # for email
from django.urls import reverse  # for email
from django.conf import settings
from django.http import JsonResponse
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, get_list_or_404
from rest_framework.authtoken.models import Token
from rest_framework import status
from mail_templated import EmailMessage
from mail_templated import send_mail
from .utils import EmailThread
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ActivationResendSerializer
import jwt
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError


class SignUpView(APIView):
    serializer_class = SignUpSerializer

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        # print user

        serializer = SignUpSerializer(data=request.data, context={'request': request})

        # validate password
        try:
            validate_password(request.data['password1'])
        except exception.ValidationError as e:
            return Response({"password": e.messages}, status=400)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        email = serializer.validated_data['email']

        # --------- send email ---------
        user_obj = get_object_or_404(User, email=email)
        token = self.get_token_for_user(user_obj)
        serializer_act = VerificationSerializer(data=request.data, context={'token': token})
        serializer_act.is_valid(raise_exception=True)
        verification = serializer_act.save()

        # ------------------------------
        return Response({
            "user": {"department": user.department.name, "email": email,
                     "gender": user.gender},
            "message": "User created successfully. Please check your email to activate your account. ",
        }, status=201)

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def put(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({'message': 'Email and code are required'}, status=status.HTTP_400_BAD_REQUEST)
        verification = Verifications.objects.filter(email=email, code=code).first()
        if not verification:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)
        if not verification.is_valid:
            verification.delete()
            return Response({'message': 'Code is expired'}, status=status.HTTP_400_BAD_REQUEST)
        verification.verify_email()
        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)


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
        payload = {
            'user_id': user_id,
            'exp': exp_time
        }

        # Generate the token using the JWT package and your Django SECRET_KEY setting
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

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


# class ConfirmEmailView():
#     pass


class ActivationConfirmView(GenericAPIView):
    serializer_class = ActivationConfirmSerializer
    permission_classes = []

    def post(self, request, token):
        # if not self.is_valid_token(token):
        #     return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user_from_token(token)
        try:
            user = Verification.objects.get(email=user)
        except Verification.DoesNotExist:
            return Response({'message': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

        if request.data.get('verification_code') != user.code:
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

    import jwt
    from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

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
            return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Please enter code verification'}, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ActivationResend(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

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
