from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('changepassword/', views.UserChangePasswordView.as_view(), name='ChangePassword'),
    path('send-reset-password-email/', views.SendPasswordResetEmailView.as_view(), name='Send-reset-password-email'),
    path('reset-password/<uid>/<token>', views.UserPasswordResetView.as_view(), name='reset-password'),
    path('verify-email/', views.VerifyEmailView.as_view()),
]