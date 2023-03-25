from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import *
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as exception


class SignUpSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email',
                  'password1', 'password2', 'gender')
        extra_kwargs = {
            'password1': {'write_only': True},
            'password1': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': ['Passwords must match.'],
            })
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            gender=validated_data['gender'],
            password=make_password(validated_data['password1'])
        )
  

        return user
    


class LoginSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError({
                'username': ['Invalid Credentials'],
            })
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password1']:
            raise serializers.ValidationError({
                'new_password1': ['Passwords must match.'],
            })
        try:
            validate_password(attrs['new_password'])
        except exception.ValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return super().validate(attrs)