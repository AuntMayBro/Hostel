from rest_framework import serializers
from .models import User

from django.utils.encoding import smart_str, force_bytes , DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .utils import Util

class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style = {'input_type':'passwerd'},write_only = True)
    class Meta :
        model = User
        fields = ['email' , 'name', 'password', 'password2', 'tc']
        extra_kwargs={
            'password':{'write_only':True}
        }
    
    #validating password and confirm password
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2 :
            raise serializers.ValidationError('password Does not match')
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    
class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    class Meta :
        model = User
        fields = ['email','password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email','name']

class ChangeUserPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style = {'input_type':'passwerd'},write_only = True)
    password2 = serializers.CharField(style = {'input_type':'passwerd'},write_only = True)
    class Meta :
        fields = ['password','[password2]']

    def validate(self, attrs):
        user = self.context.get('user')
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2 :
            raise serializers.ValidationError('password Does not match')
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            # build reset link (example: http://localhost:3000/reset-password/uid/token)
            link = f"http://localhost:3000/reset-password/{uid}/{token}"

            # send email here using Django Email backend or any service
            body = 'Click Link To Reset Your Password'+ link
            data = {
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email,
            }
            Util.send_email(data)
            print(f"Reset link: {link}")  # For now, just print. Replace with actual email logic.
            return attrs
        else:
            raise serializers.ValidationError("Email is Not Registered")


class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style = {'input_type':'passwerd'},write_only = True)
    password2 = serializers.CharField(style = {'input_type':'passwerd'},write_only = True)
    class Meta :
        fields = ['password','password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Passwords do not match.")

            uid = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or expired.")

            user.set_password(password)
            user.save()
            return attrs

        except DjangoUnicodeDecodeError:
            raise serializers.ValidationError("Token is invalid or has expired.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
