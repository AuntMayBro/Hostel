from django.urls import path, include
from .views import DirectorRegistrationView

urlpatterns = [
    path('register/', DirectorRegistrationView.as_view(), name='director-register'),
]