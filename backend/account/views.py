from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangeUserPasswordSerializer,
    SendPasswordResetEmailSerializer,
    UserPasswordResetSerializer
)
from .models import User
from django.contrib.auth import authenticate
from .renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# Create token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# User Registration View
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    # renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token': token, 'msg': 'Registration Successful'}, status=status.HTTP_201_CREATED)

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
            # Set user id in session
            request.session['user_id'] = user.id
            request.session['user_email'] = user.email

            token = get_tokens_for_user(user)
            return Response({'token': token, 'msg': 'Login Successful'}, status=status.HTTP_200_OK)

        return Response({'msg': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

    
# LogOut View
class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)
    # renderer_classes = [UserRenderer]
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
    # renderer_classes = [UserRenderer]
    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# User Change Password View
class UserChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    # renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = ChangeUserPasswordSerializer(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)

# Send Password Reset Email View
class SendPasswordResetEmailView(APIView):
    # renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Email to Change Password Sent'}, status=status.HTTP_200_OK)

# User Password Reset View
class UserPasswordResetView(APIView):
    # renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid': uid, 'token': token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg': 'Password Reset Successfully'}, status=status.HTTP_200_OK)
