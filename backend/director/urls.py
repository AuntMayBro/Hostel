from django.urls import path, include
from .views import  *

urlpatterns = [
    # Director Urls
    path('register/', DirectorCreateView.as_view(), name='director-create'),
    path('<int:pk>/', DirectorDetailView.as_view(), name='director-detail'),
    path('<int:pk>/update/', DirectorUpdateView.as_view(), name='director-update'),

    #Courses and Branches
    path('courses/', InstituteCourseListCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),

    path('branches/', CourseBranchListCreateView.as_view(), name='branch-create'),
    path('branches/<int:pk>/', BranchDetailView.as_view(), name='branch-detail'),
]