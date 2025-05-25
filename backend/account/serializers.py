from rest_framework import serializers
from .models import User
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import  urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password # Django's built-in password validators
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from django.utils import timezone
from django.contrib.sessions.models import Session



# user registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# User login Serializer
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email', 'password']

# User Profile Serializer
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email'] 

# Change Password Serializer
class ChangeUserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        error_messages={
            'required': 'Old password is required.',
        }
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        error_messages={
            'required': 'New password is required.',
        }
    )

    def validate(self, attrs):
        user = self.context.get('user')
        if not user:
            raise serializers.ValidationError("User context not provided.")
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')

        if not user.check_password(old_password):
            raise serializers.ValidationError({'old_password': 'Old password is not correct.'})

        if old_password == new_password:
            raise serializers.ValidationError({'new_password': 'New password cannot be the same as the old password.'})

        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
        user.save()

# Send Reset Password Email Serializer
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }
    )
    _user = None

    def validate_email(self, value):
        user = User.objects.filter(email=value).first()
        self._user = user
        return value

    @property
    def user(self):
        return self._user

    class Meta:
        fields = ['email']

# User Password Reset by Email Serializer 
class UserPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        min_length=getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [{}])[0].get('OPTIONS', {}).get('min_length', 8), # Dynamic min_length
        error_messages={
            'required': 'New password is required.',
            'min_length': 'New password must be at least %(min_length)d characters long.'
        }
    )
    _user = None
    def validate(self, attrs):
        uid = self.context.get('uid')
        token = self.context.get('token')
        new_password = attrs.get('new_password')

        if not uid or not token:
            raise serializers.ValidationError("Missing UID or token.", code='missing_credentials')
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
            self._user = user
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
            raise serializers.ValidationError("Invalid or expired password reset link.", code='invalid_link')
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid or expired password reset link.", code='invalid_link')
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)}, code='password_strength')
        return attrs

    def save(self, **kwargs):
        user = self._user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        Session.objects.filter(expire_date__gte=timezone.now(), session_key__in=Session.objects.filter(pk=user.pk)).delete() # This needs adjustment for session key mapping, simpler is just to clear all for user
        return user
    
# Verify Email Serializer
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, max_length=6)
