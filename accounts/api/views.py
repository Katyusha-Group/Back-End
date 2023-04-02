from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from .serializers import LoginSerializer
from ..models import User
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

class SignUpView(GenericAPIView):
    serializer_class = SignUpSerializer

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = SignUpSerializer(
            data=request.data, context={'request': request})

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
        message = EmailMessage( 'email/activation_email.tpl', {'token': token}, 'asad@asd.com', to = [email])
        EmailThread(message).start()
    
   
        # ------------------------------
        return Response({
            "user": {"username": user.username,
                     "email": email,
                     "gender": user.gender},
            "message": "User created successfully. Now perform Login to get your token",
        })
        

    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
        
    




class LoginView(ObtainAuthToken):
    serializer_class = LoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({'token': token.key,
                         'user_id': user.id,
                         'username': user.username,
                         'email': user.email,
                         })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated] # permission_classes = []

    
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


import jwt 
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

class ActivationConfirmView(APIView):
    def get(self, request, token,*args, **kwargs):
        
        # decode token  -> id user
        # get user
        # is_email_verified = True
        token = self.decode_token(token)
        user = User.objects.get(id=token['user_id'])
        if user.is_email_verified:
            return Response({"message": "Email has already been verified"}, status=400)
        user.is_email_verified = True
        user.save()
        return Response({"message": "Email has been verified"}, status=200)



    def decode_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed({'detail': 'Token has expired'})
        except jwt.InvalidSignatureError:
            raise AuthenticationFailed({'detail': 'Token is not valid'})
        return payload
        # except jwt.exceptions.ExpiredSignatureError:
        #     raise AuthenticationFailed('Token has expired')
        # except jwt.exceptions.DecodeError:
        #     raise AuthenticationFailed('Token is invalid')
        # except jwt.exceptions.InvalidTokenError:
        #     raise AuthenticationFailed('Token is invalid')       


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



        

class ActivationResend(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = ActivationResendSerializer(data=request.data)
        if serializer.is_valid():
            user_obj = serializer.validated_data['user']
            token = self.get_token_for_user(user_obj)
            email_obj = EmailMessage( 'email/activation_email.tpl', {'token': token}, 'asad@asd.com', to = [user_obj.email])
            EmailThread(email_obj).start()
            return Response({"message": "email sent"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    def get_token_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)