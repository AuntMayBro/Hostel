from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import timedelta, datetime
import smtplib
import json
import base64
from django.conf import settings

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import APIException, ValidationError, AuthenticationFailed, ParseError
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError, ExpiredSignatureError

from .emails import sendPasswordResetEmail, sendRegistrationMail
from account.serializers import ( 
    UserRegistrationSerializer, UserProfileSerializer,
    ChangeUserPasswordSerializer, SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer, VerifyEmailSerializer, AdminLoginSerializer,
    StudentLoginSerializer, MyTokenObtainPairSerializer
)

from .models import UserRole

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class EmailSendError(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Email could not be sent. Please contact support or try again later.'
    default_code = 'email_send_error'


class UserNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'User not found.'
    default_code = 'user_not_found'

class GetSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]  # optional

    def _decode_token_expiration(self, token_string, token_type="access"):
        try:
            token_cls = AccessToken if token_type == "access" else RefreshToken
            token_obj = token_cls(token_string)
            return timezone.datetime.fromtimestamp(token_obj["exp"], tz=timezone.utc)
        except Exception as e:
            print(f"[Token Decode Error] {token_type.title()} Token: {e}")
            return None

    def get(self, request):
        user = request.user

        if not user or not user.is_authenticated:
            raise AuthenticationFailed("Authentication credentials were not provided or invalid.")

        access_token_string = None
        refresh_token_string = request.COOKIES.get('refresh')

        if request.auth:
            access_token_string = str(request.auth)
        else:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                access_token_string = auth_header.replace("Bearer ", "")
            if not access_token_string:
                raise AuthenticationFailed("Access token missing or malformed in Authorization header.")

        # Decode expiration
        access_exp = self._decode_token_expiration(access_token_string, "access")
        refresh_exp = self._decode_token_expiration(refresh_token_string, "refresh") if refresh_token_string else None

        # Build response
        response_data = {
            "session": {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": getattr(user, "role", "user")
                },
                "access_token": access_token_string,
                "access_expires_at": access_exp,
                "refresh_token": refresh_token_string,
                "refresh_expires_at": refresh_exp,
                "authenticated": True
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            if email and User.objects.filter(email=email).exists():
                return Response({"msg": -1, "error": "User with this email already exists."},
                                status=status.HTTP_400_BAD_REQUEST)

            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response({"msg": -1, "errors": serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()

            verification_code = get_random_string(length=6, allowed_chars='0123456789')
            user.verification_code = verification_code
            user.verification_code_expires_at = timezone.now() + timedelta(
                minutes=getattr(settings, 'VERIFICATION_CODE_EXPIRY_MINUTES', 15)
            )
            user.save(update_fields=['verification_code', 'verification_code_expires_at'])

            try:
                sendRegistrationMail(user)
            except smtplib.SMTPException as e:
                return Response({"msg": 0, "error": f"SMTP Error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                return Response({"msg": 0, "error": f"Unexpected email error: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "msg": 1,
                "msg2": "Registration successful. Please check your email for the verification code to activate your account."
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"msg": 0, "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class UserLoginView(generics.GenericAPIView):
#     serializer_class = UserLoginSerializer
#     permission_classes = [AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
#         email = serializer.validated_data.get('email')
#         password = serializer.validated_data.get('password')
        
#         user = authenticate(request, email=email, password=password)
        
#         if user is not None:
#             if not user.is_active:
#                 return Response({'detail': 'Account not activated. Please verify your email.'}, status=status.HTTP_403_FORBIDDEN)

#             tokens = get_tokens_for_user(user)
#             return Response({
#                 'tokens': tokens, 
#                 'user_id': user.id,
#                 'email': user.email,
#                 'role': user.role,
#                 'msg': 'Login Successful'
#             }, status=status.HTTP_200_OK)
        
#         return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)


class BaseLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def authenticate_and_login(self, request, email, password, expected_role=None):
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if not user.is_active:
                return Response({'detail': 'Account not activated. Please verify your email.'}, status=status.HTTP_403_FORBIDDEN)
            
            if expected_role and user.role != expected_role:
                return Response({'detail': f'Unauthorized: You do not have {expected_role} privileges.'}, status=status.HTTP_403_FORBIDDEN)
            
            tokens = get_tokens_for_user(user)
            return Response({
                'tokens': tokens, 
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'msg': 'Login Successful'
            }, status=status.HTTP_200_OK)
        
        return Response({'detail': 'Invalid email or password.'}, status=status.HTTP_401_UNAUTHORIZED)

class StudentLoginView(BaseLoginView):
    serializer_class = StudentLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        
        return self.authenticate_and_login(request, email, password, expected_role=UserRole.STUDENT)

class AdminLoginView(BaseLoginView):
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        role = serializer.validated_data.get('role')

        return self.authenticate_and_login(request, email, password, expected_role=role)

class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"msg": "Logged out successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"msg": "Invalid refresh token", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserChangePasswordView(generics.UpdateAPIView): 
    serializer_class = ChangeUserPasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        serializer.save() 
        update_session_auth_hash(request, user)
        return Response({'msg': 'Password changed successfully.'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(generics.GenericAPIView):
    serializer_class = SendPasswordResetEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        user = User.objects.filter(email=email, is_active=True).first()

        if user is None :
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )    
        
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
 
            frontend_reset_url = getattr(settings, 'FRONTEND_PASSWORD_RESET_URL', 'http://127.0.0.1:8000/api/user/reset-password') 
            reset_link = f"{frontend_reset_url}/{uid}/{token}/"
            
            try:
                sendPasswordResetEmail(user, reset_link)
            except Exception as e:
                print(f"Error sending password reset email to {user.email}: {e}")
        

        return Response(
            {'msg': 'If an account with that email exists and is active, a password reset link has been sent.'},
            status=status.HTTP_200_OK
        )

class UserPasswordResetView(generics.GenericAPIView):
    serializer_class = UserPasswordResetSerializer
    permission_classes = [AllowAny]

    def post(self, request, uid, token, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, 
            context={'uid': uid, 'token': token}
        )
        serializer.is_valid(raise_exception=True) 
        serializer.save()
        return Response({'msg': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
    
class VerifyEmailView(generics.GenericAPIView): 
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) 
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save() # Serializer's save method handles activation
        
        tokens = get_tokens_for_user(user)
        return Response({
            'tokens': tokens,
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'msg': 'Email verified successfully. Account activated.'
        }, status=status.HTTP_200_OK)