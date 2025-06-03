from django.urls import path
from .views import (
    DirectorCreateView,
    DirectorDetailView,
    InstituteListView,
    InstituteDetailView,
    CourseListCreateView,
    CourseDetailView,
    BranchListCreateView,
    BranchDetailView,
    DirectorHostelListCreateView,
    DirectorHostelDetailView,
    # HostelCreateAPIView
)

urlpatterns = [
    # Director's Url
    path('register/', DirectorCreateView.as_view(), name='director-register'),
    path('<int:pk>/', DirectorDetailView.as_view(), name='director-detail'),

    # Institute's Url
    path('institute/', InstituteListView.as_view(), name='institute-list'),
    path('institute/<int:pk>/', InstituteDetailView.as_view(), name='institute-detail'),

    # Coursees' Url
    path('courses/', CourseListCreateView.as_view(), name='course-list-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    # Branches' Url
    path('branches/', BranchListCreateView.as_view(), name='branch-list-create'),
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),

    # Hostel's Url
    path('create-hostel/', DirectorHostelListCreateView.as_view(), name='director-hostel-list-create'),
    path('hostel/<int:pk>/', DirectorHostelDetailView.as_view(), name='director-hostel-detail'),

    # path('hostel/create/', HostelCreateAPIView.as_view(), name='hostel-create'),
]