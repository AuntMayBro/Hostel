# accounts/views.py

from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,UserLoginSerializer,UserProfileSerializer,ChangeUserPasswordSerializer,
    SendPasswordResetEmailSerializer,UserPasswordResetSerializer,VerifyEmailSerializer
)
from .models import User 
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from django.utils.crypto import get_random_string
from django.conf import settings
import smtplib
from rest_framework.exceptions import APIException 
from django.utils import timezone
from datetime import timedelta
from .emails import sendRegistrationMail ,sendPasswordResetEmail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import update_session_auth_hash

# token
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Custom exception for email sending failures
class EmailSendError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Email could not be sent. Please contact support or try again later.'
    default_code = 'email_send_error'

# User Registration View
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer

    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        verification_code = get_random_string(length=6, allowed_chars='0123456789')
        user.verification_code = verification_code
        user.verification_code_expires_at = timezone.now() + timedelta(minutes=15)
        user.save()

        try:
            sendRegistrationMail(user)
            print(f"DEBUG: Email attempted to send successfully to {user.email}")
        except smtplib.SMTPException as e:
            print(f"SMTP Error sending verification email to {user.email}: {e}")
            raise EmailSendError()
        except Exception as e:
            print(f"Unexpected Error sending verification email to {user.email}: {e}")
            raise EmailSendError()

        return Response({
            "msg": "Registration successful. Please check your email for the verification code to activate your account."
        }, status=status.HTTP_201_CREATED)

# User Login View
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email
            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Successful'}, status=status.HTTP_200_OK)
        return Response({'msg': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

# LogOut View 
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or token already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)

# User Profile View 
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# User Change Password View
class UserChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangeUserPasswordSerializer
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        update_session_auth_hash(request, request.user)
        return Response({'message': ''}, status=status.HTTP_200_OK)
        return Response({'token': token, 'msg': 'Password changed successfully.'}, status=status.HTTP_200_OK)

# Send Password Reset Email View 
class SendPasswordResetEmailView(generics.GenericAPIView):
    serializer_class = SendPasswordResetEmailSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"http://localhost:8000/api/user/reset-password/{uid}/{token}"
            try:
                sendPasswordResetEmail(user , reset_link)
                print(f"DEBUG: Email attempted to send successfully to {user.email}")
            except Exception as e:
                print(f"Error sending password reset email to {user.email}: {e}")
                raise EmailSendError()
            
        return Response(
            {'message': 'If an account with that email exists, a password reset link has been sent to it.'},
            status=status.HTTP_200_OK
        )

# User Password Reset View 
class UserPasswordResetView(generics.GenericAPIView):
    serializer_class = UserPasswordResetSerializer
    def post(self, request, uid, token, format=None):
        serializer = self.serializer_class(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True) 
        serializer.save()
        return Response({'token': token, 'msg': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

# Email Varification View    
class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data) 
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')
        code = serializer.validated_data.get('code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or code."}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_active:
            return Response({"msg": "Account already activated"}, status=status.HTTP_400_BAD_REQUEST)

        if user.verification_code != code:
            return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

        if user.verification_code_expires_at and timezone.now() > user.verification_code_expires_at:
            return Response({"error": "Verification code has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.verification_code = None
        user.verification_code_expires_at = None
        user.save()
        token = get_tokens_for_user(user)
        return Response({'token': token, 'msg': 'Email verified successfully'}, status=status.HTTP_200_OK)