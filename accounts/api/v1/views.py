from rest_framework import generics
from rest_framework.response import Response
from .serializers import *
from ...models import User
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

class SignUpView(APIView):
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
        # --------- send email ---------
    
        # ------------------------------
        return Response({
            "user": {"username": user.username,
                     "email": user.email,
                     "gender": user.gender},
            "message": "User created successfully. Now perform Login to get your token",
        })




class LoginView(APIView):
    serializer_class = LoginSerializer
    
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({
                "message": "Invalid Credentials"
            }, status=400)
        
        # if not user.is_email_verified:
        #     return Response({
        #         "message": "Email is not verified"
        #     }, status=400)
        
        login(request, user)
        token = Token.objects.get_or_create(user=user)[0].key,

        

        return Response({
            "token" : token,
            "message": "Login Successful"
            
        }, status=200)




class LogoutView(APIView):
    permission_classes = []

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


class ChangePasswordView(generics.UpdateAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj
    
    def update(self, request, *args, **kwargs):
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

class TestView(generics.GenericAPIView):
    def get(self, request):
        message = EmailMessage('email/hello.tpl', {'user': 'ali'}, 'ali.288@gmail.com',
                       to=['marg@gmail.com'])           
        return Response({
            "message": "Test Successful"
        }, status=200)
    





        
    