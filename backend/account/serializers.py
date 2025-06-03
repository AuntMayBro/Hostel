from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.conf import settings
from django.utils import timezone
from django.contrib.sessions.models import Session

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'role'] 
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

# User login Serializer
class UserLoginSerializer(serializers.Serializer): # Changed to serializers.Serializer for custom auth
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True
    )

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
    )
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
    )

    def validate_old_password(self, value):
        user = self.context.get('user')
        if not user or not user.check_password(value):
            raise serializers.ValidationError('Old password is not correct.')
        return value

    def validate_new_password(self, value):
        user = self.context.get('user')
        try:
            validate_password(value, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({'new_password': 'New password cannot be the same as the old password.'})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
    
    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

# Send Reset Password Email Serializer

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email is required.',
            'invalid': 'Enter a valid email address.'
        }                           
    )

    def validate_email(self, value):
        if not User.objects.filter(email=value, is_active=True).exists():
            pass
        return value

# User Password Reset by Email Serializer 
class UserPasswordResetSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        required=True,
    )

    def validate_new_password(self, value):
        uid = self.context.get('uid')
        token = self.context.get('token')
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
            user = None

        if user: 
            try:
                validate_password(value, user=user)
            except DjangoValidationError as e:
                raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        uid = self.context.get('uid')
        token = self.context.get('token')
        
        if not uid or not token:
            raise serializers.ValidationError("Missing UID or token.", code='missing_credentials')
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id, is_active=True) 
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
            raise serializers.ValidationError("Invalid or expired password reset link.", code='invalid_link')
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid or expired password reset link.", code='invalid_token')
        
        self.context['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        for session in Session.objects.filter(expire_date__gte=timezone.now()):
            session_data = session.get_decoded()
            if str(user.pk) == session_data.get('_auth_user_id'):
                session.delete()
        return user
    
# Verify Email Serializer
class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(required=True, max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        code = attrs.get('code')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"detail": "Invalid email or verification code."})

        if user.is_active:
            raise serializers.ValidationError({"detail": "Account already activated."})

        if user.verification_code != code:
            raise serializers.ValidationError({"code": "Invalid verification code."})

        if user.verification_code_expires_at and timezone.now() > user.verification_code_expires_at:
            raise serializers.ValidationError({"code": "Verification code has expired. Please request a new one."})
        
        self.context['user'] = user
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.is_active = True
        user.verification_code = None
        user.verification_code_expires_at = None
        user.save()
        return user
