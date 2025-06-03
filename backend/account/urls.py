from django.urls import path
from .views import (
    UserRegistrationView,
    UserLoginView,
    LogoutView,
    UserProfileView,
    UserChangePasswordView,
    SendPasswordResetEmailView,
    UserPasswordResetView,
    VerifyEmailView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='user-logout'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', UserChangePasswordView.as_view(), name='user-change-password'),
    path('send-reset-password-email/', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    path('reset-password/<str:uid>/<str:token>/', UserPasswordResetView.as_view(), name='user-password-reset'),
    path('verify-email/', VerifyEmailView.as_view(), name='user-verify-email'),
]