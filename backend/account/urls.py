from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    StudentLoginView,
    AdminLoginView,
    LogoutView,
    UserProfileView,
    UserChangePasswordView,
    SendPasswordResetEmailView,
    UserPasswordResetView,
    VerifyEmailView,
    GetSessionView,
    ResendOTPView
)




urlpatterns = [
    
    path('session/', GetSessionView.as_view(), name='get-session'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Refister URLs
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('verify-email/', VerifyEmailView.as_view(), name='user-verify-email'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),

    # Login Logout URLs
    path('login/student/', StudentLoginView.as_view(), name='student-login'), 
    path('login/admin/', AdminLoginView.as_view(), name='admin-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),

    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # Change Password URLs
    path('change-password/', UserChangePasswordView.as_view(), name='user-change-password'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<str:uid>/<str:token>/', UserPasswordResetView.as_view(), name='user-password-reset'),
]