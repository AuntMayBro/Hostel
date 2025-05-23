from rest_framework import serializers
from .models import User

from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta:
        model = User
        fields = ['email', 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']  # Removed 'name'

class ChangeUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        user = self.context.get('user')
        user.set_password(attrs.get('password'))
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            link = f"http://localhost:3000/reset-password/{uid}/{token}"
            body = 'Click Link To Reset Your Password: ' + link
            data = {
                'subject': 'Reset Your Password',
                'body': body,
                'to_email': user.email,
            }
            Util.send_email(data)
            print(f"Reset link: {link}")
            return attrs
        else:
            raise serializers.ValidationError("Email is not registered")

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            uid = self.context.get('uid')
            token = self.context.get('token')

            uid = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or expired.")

            user.set_password(password)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError("Token is invalid or has expired.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
