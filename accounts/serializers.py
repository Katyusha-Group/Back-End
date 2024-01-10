from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.core import exceptions as exception
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from accounts.models import User, Wallet, WalletTransaction
from utils.variables import project_variables


# user serializer
class UserSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='department.name')
    class Meta:
        model = User
        fields = ["username", "gender", "department", "email", "is_email_verified", "has_verification_tries_reset", "verification_tries_count", "id" ]

class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(
        validators=[
            RegexValidator(
                regex="^(?=.{6,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_... .])$",
                message="Username must be 6-20 characters long, cannot start or end with a period or underscore"
                        ", and cannot contain two consecutive periods or underscores."
            )
        ]
    )
    name = serializers.CharField(required=True)
    password1 = serializers.CharField(
        style={'input_type': 'password'},
        validators=[password_validation.validate_password],
        write_only=True
    )
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'name',
                  'password1', 'password2', 'gender', 'department')
        extra_kwargs = {
            'password1': {'write_only': True},
            'password2': {'write_only': True},
        }

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')

        # Check if the username already exists
        existing_user = User.objects.filter(username__iexact=username).first()


        if existing_user:
            # If the username exists, check if the email matches
            if existing_user.email.lower() == email.lower():
                return data
            else:
                # If the username exists and the email doesn't match, raise an error
                raise serializers.ValidationError("This username is already taken.")
        else:
            return data
    def validate_password2(self, value):
        if value != self.initial_data.get('password1'):
            raise serializers.ValidationError('Passwords must match.')
        return value
    def validate_password(self, value):
        if value != self.initial_data.get('password2'):
            raise serializers.ValidationError('Passwords must match.')
        password_validation.validate_password(value)
        return value

    def validate_email(self, value):
        user = User.objects.filter(email__iexact=value)
        if user.exists():
            user = user.first()
            if user.is_email_verified:
                raise serializers.ValidationError("Email already exists.")
            if user.verification_tries_count >= project_variables.MAX_VERIFICATION_TRIES:
                raise serializers.ValidationError("You have reached the maximum number of registration tries.")
            if user.username != self.initial_data.get('username'):
                raise serializers.ValidationError("Email already exists.")
        return str.lower(value)



class LoginSerializer(serializers.Serializer):
    email_or_username = serializers.CharField(
        label=_("Email or Username"),
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

    def get_lookup_field(self, value):
        return 'email__iexact' if '@' in value else 'username__iexact'

    def validate(self, attrs):
        email_or_username = attrs.get('email_or_username', None)
        password = attrs.get('password', None)

        if email_or_username and password:
            lookup_field = self.get_lookup_field(email_or_username)
            email_or_username = self.validate_email_or_username(email_or_username)
            user = User.objects.get(**{lookup_field: email_or_username})

            if not user.check_password(password):
                msg = _('Incorrect password.')
                raise serializers.ValidationError(msg, code='authorization')


            if not user.is_email_verified:
                raise serializers.ValidationError({"detail": "User is not verified."})


            attrs['user'] = user
        else:
            msg = _('Must include "email_or_username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        return attrs
    def validate_email_or_username(self, value):
        if '@' in value:
            lookup_field = 'email__iexact'
            msg = _('Email does not exist.')
        else:
            lookup_field = 'username__iexact'
            msg = _('Username does not exist.')

        user_exists = User.objects.filter(**{lookup_field: value}).exists()
        if not user_exists:
            raise serializers.ValidationError(msg)

        return str.lower(value)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password1 = serializers.CharField(required=True, write_only=True)

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
        return attrs


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
            user = User.objects.get(email__iexact=email)
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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError("New password and confirm password do not match.")

        # Validate password complexity using Django's built-in password validators
        try:
            validate_password(new_password)
        except serializers.ValidationError as validation_error:
            raise serializers.ValidationError({"new_password": validation_error})

        return attrs


class CodeVerificationSerializer(serializers.Serializer):
    verification_code = serializers.CharField(max_length=4, min_length=4)


class ChangePasswordloginSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Invalid current password.")
        return value

    def validate(self, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        # Additional validation logic if needed
        # For example, you can check password complexity requirements

        if current_password == new_password:
            raise serializers.ValidationError("New password must be different from the current password.")

        return data
