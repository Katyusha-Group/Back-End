from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from accounts.models import *
from datetime import datetime, timedelta
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as exception
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email',
                  'password1', 'password2', 'gender', 'department')
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({
                'password2': ['Passwords must match.'],
            })
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):

        username = attrs.get('username', None)
        password = attrs.get('password', None)

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Does not exist or wrong password.')
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_email_verified:
                raise serializers.ValidationError({"detail": "user is not verified."})
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # def validate(self, attrs):
    #     data = super().validate(attrs)

    #     refresh = self.get_token(self.user)

    #     data['refresh'] = str(refresh)
    #     data['access'] = str(refresh.access_token)

    #     data['user'] = UserSerializer(self.user).data

    #     return data
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        if not self.user.is_email_verified:
            raise serializers.ValidationError({"detail": "user is not verified."})

        validated_data['email'] = self.user.email
        validated_data['id'] = self.user.id
        return validated_data


class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email', None)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "user does not exist."})

        if user.is_email_verified:
            raise serializers.ValidationError({"detail": "user is already verified."})

        attrs['user'] = user
        return attrs


class ActivationConfirmSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=4, min_length=4)


class SimpleUserSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='email')

    class Meta:
        model = User
        fields = ['user_email']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'department', 'gender']


class WalletSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_representation = representation.pop('user')
        for key in user_representation:
            representation[key] = user_representation[key]
        return representation

    user = SimpleUserSerializer(read_only=True)
    balance = serializers.DecimalField(decimal_places=0, max_digits=10, read_only=True)

    class Meta:
        model = Wallet
        fields = ['user', 'balance']


class ModifyWalletSerializer(serializers.Serializer):
    amount = serializers.IntegerField()

    def update(self, instance, validated_data):
        amount = validated_data['amount']
        if amount < 0 and instance.balance < abs(amount):
            raise serializers.ValidationError({"detail": "insufficient funds."})
        instance.balance += validated_data['amount']
        instance.save()
        return instance


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WalletTransaction
        fields = ['amount', 'transaction_type', 'ref_code', 'applied_at']
