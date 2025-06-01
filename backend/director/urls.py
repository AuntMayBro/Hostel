from django.urls import path, include
from .views import  DirectorCreateView , DirectorDetailView , DirectorUpdateView

urlpatterns = [
    # Director Urls
    path('register/', DirectorCreateView.as_view(), name='director-create'),
    path('<int:pk>/', DirectorDetailView.as_view(), name='director-detail'),
    path('<int:pk>/update/', DirectorUpdateView.as_view(), name='director-update'),
]