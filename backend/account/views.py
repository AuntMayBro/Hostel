from django.contrib.auth import authenticate, get_user_model, update_session_auth_hash
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import timedelta
import smtplib
from django.conf import settings

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import APIException, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from .emails import sendPasswordResetEmail, sendRegistrationMail
from account.serializers import ( 
    UserRegistrationSerializer, UserProfileSerializer,
    ChangeUserPasswordSerializer, SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer, VerifyEmailSerializer, AdminLoginSerializer,
    StudentLoginSerializer
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


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        verification_code = get_random_string(length=6, allowed_chars='0123456789')
        user.verification_code = verification_code
        user.verification_code_expires_at = timezone.now() + timedelta(minutes=settings.VERIFICATION_CODE_EXPIRY_MINUTES if hasattr(settings, 'VERIFICATION_CODE_EXPIRY_MINUTES') else 15)
        user.save(update_fields=['verification_code', 'verification_code_expires_at'])

        try:
            sendRegistrationMail(user)
        except smtplib.SMTPException as e:
            raise EmailSendError(detail=f"SMTP Error: {str(e)}")
        except Exception as e:
            raise EmailSendError(detail=f"Unexpected email error: {str(e)}")

        return Response({
            "msg": "Registration successful. Please check your email for the verification code to activate your account."
        }, status=status.HTTP_201_CREATED)

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
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"msg": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e: 
            return Response({"detail": "Invalid token or token already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)


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