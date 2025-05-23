from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import UserRegistrationSerializer ,UserLoginSerializer, UserProfileSerializer, ChangeUserPasswordSerializer, SendPasswordResetEmailSerializer, UserPasswordResetSerializer
from rest_framework import generics
from .models import User
from django.contrib.auth import login, authenticate
from .renderers import UserRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore

#create token manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    # renderer_classes = [UserRenderer]
    def post(self , request ,format = None):
        serializer = UserRegistrationSerializer(data = request.data)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token,'msg':'Resistration SuccesFull'},status = status.HTTP_201_CREATED)
        

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    # renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(request, email=email, password=password)  # depends on custom backend

            if user is not None:
                token = get_tokens_for_user(user)
                return Response({'token':token,'msg': 'Login Successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'msg': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # user = serializer.validated_data['user']
            # login(request, user)  # optional: logs the user into the session
            # return Response({
            #     "message": "Login successful",
            #     "username": user.username,
            #     "email": user.email,
            # }, status=status.HTTP_200_OK)

class UserProfileView(APIView):
    # renderer_classes = [UserRenderer]
    permission_classes = ['IsAuthenticated']
    def get(self, request, format=None):
        serializer = UserProfileSerializer
        return Response(serializer.data , status=status.HTTP_200_OK)
    
class UserChangePasswordView(APIView):
    # renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
        serializer = ChangeUserPasswordSerializer(data = request.data, context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({'msg': 'Password Changed Successfully'}, status=status.HTTP_200_OK)
        Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendPasswordResetEmailView(APIView):
    # renderer_classes = [UserRenderer]
     def post(self, request, format=None):
         serializer = SendPasswordResetEmailSerializer(data=serializer.data)
         if serializer.is_valid(raise_exception=True):
             return Response({'msg': 'Email to Change Password Sent'}, status=status.HTTP_200_OK)
         
class UserPasswordResetView(APIView):
    # renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data = request.data , context = {'uid':uid, 'token':token})
        if serializer.is_valid(raise_exception=True):
             return Response({'msg': 'password Reset Sucessfully'}, status=status.HTTP_200_OK)
        Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)