from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken

from director.models import Director, Institute, Course, Branch
from director.serializers import (
    DirectorRegistrationSerializer, CourseSerializer, BranchSerializer, InstituteSerializer
)
from hostel.models import Hostel 
from hostel.serializers import HostelSerializer

from director.permissions import IsDirectorOwnerOrReadOnly

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your Views here


class DirectorCreateView(generics.CreateAPIView):
    serializer_class = DirectorRegistrationSerializer
    permission_classes = [permissions.AllowAny] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        director = serializer.save()

        tokens = get_tokens_for_user(director.user)

        return Response({
            "msg": "Director registered successfully. Institute created.",
            "director_id": director.id,
            "user_id": director.user.id,
            "institute_id": director.institute.id,
            "tokens": tokens,
        }, status=status.HTTP_201_CREATED)

class DirectorDetailView(generics.RetrieveUpdateDestroyAPIView): 
    queryset = Director.objects.select_related('user', 'institute').all()
    serializer_class = DirectorRegistrationSerializer 
    # permission_classes = [permissions.IsAuthenticated, IsDirectorOwnerOrReadOnly] 
    lookup_field = 'pk'

    # def get_permissions(self):
    #     if self.request.method in permissions.SAFE_METHODS:
    #         return [permissions.IsAuthenticated()]
    #     return [permissions.IsAuthenticated(), IsDirectorOwnerOrReadOnly()]


class InstituteListView(generics.ListAPIView):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [permissions.IsAuthenticated] # Adjust as needed

class InstituteDetailView(generics.RetrieveAPIView):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer
    permission_classes = [permissions.IsAuthenticated]

class CourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Course.objects.select_related('institute').all()
        if hasattr(user, 'director_profile'):
            return Course.objects.filter(institute=user.director_profile.institute).select_related('institute')
        return Course.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        institute_from_payload = serializer.validated_data.get('institute')

        if not hasattr(user, 'director_profile') and not user.is_superuser:
            raise PermissionDenied("You do not have permission to create courses.")

        if hasattr(user, 'director_profile'):
            if institute_from_payload != user.director_profile.institute:
                raise ValidationError(
                    {"institute": "You can only create courses for your assigned institute."}
                )
            serializer.save(institute=user.director_profile.institute)
        elif user.is_superuser:
            if not institute_from_payload:
                raise ValidationError({"institute": "Institute is required for superuser."})
            serializer.save() 
        else:
            raise PermissionDenied("Action not allowed.")


class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.select_related('institute').all()
    serializer_class = CourseSerializer
    # permission_classes = [permissions.IsAuthenticated] 

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not user.is_superuser and hasattr(user, 'director_profile'):
            if obj.institute != user.director_profile.institute:
                raise PermissionDenied("You do not have permission to access this course.")
        elif not user.is_superuser:
             raise PermissionDenied("You do not have permission to access this course.")
        return obj


class BranchListCreateView(generics.ListCreateAPIView):
    serializer_class = BranchSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course_id')
        
        if not course_id:
            if user.is_superuser:
                return Branch.objects.select_related('course__institute').all()
            if hasattr(user, 'director_profile'):
                return Branch.objects.filter(course__institute=user.director_profile.institute).select_related('course__institute')
            return Branch.objects.none()

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            raise ValidationError({"course_id": "Invalid course ID."})

        if not user.is_superuser and hasattr(user, 'director_profile'):
            if course.institute != user.director_profile.institute:
                raise PermissionDenied("You can only view branches for courses in your institute.")
        elif not user.is_superuser:
            raise PermissionDenied("Permission denied.")
            
        return Branch.objects.filter(course=course).select_related('course__institute')

    def perform_create(self, serializer):
        user = self.request.user
        course_from_payload = serializer.validated_data.get('course')

        if not hasattr(user, 'director_profile') and not user.is_superuser:
            raise PermissionDenied("You do not have permission to create branches.")

        if not course_from_payload:
            raise ValidationError({"course": "Course is required to create a branch."})

        if hasattr(user, 'director_profile'):
            if course_from_payload.institute != user.director_profile.institute:
                raise ValidationError(
                    {"course": "You can only create branches for courses in your assigned institute."}
                )
        elif user.is_superuser:
            pass 
        else:
            raise PermissionDenied("Action not allowed.")
        
        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request 
        institute_id = self.kwargs.get('institute_pk')
        if institute_id:
           context['institute_id'] = institute_id
        return context


class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.select_related('course__institute').all()
    serializer_class = BranchSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not user.is_superuser and hasattr(user, 'director_profile'):
            if obj.course.institute != user.director_profile.institute:
                raise PermissionDenied("You do not have permission to access this branch.")
        elif not user.is_superuser:
            raise PermissionDenied("You do not have permission to access this branch.")
        return obj


# class HostelCreateAPIView(generics.CreateAPIView):
#     queryset = Hostel.objects.all()
#     serializer_class = HostelSerializer
#     # permission_classes = [IsAuthenticated]

#     def handle_exception(self, exc):
#         if isinstance(exc, ValidationError):
#             return super().handle_exception(exc)
#         return super().handle_exception(exc)

#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['request'] = self.request
#         return context


class DirectorHostelListCreateView(generics.ListCreateAPIView):
    serializer_class = HostelSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'director_profile'):
            return Hostel.objects.filter(institute=user.director_profile.institute).select_related('institute', 'director', 'manager__user')
        elif user.is_superuser:
            return Hostel.objects.all().select_related('institute', 'director', 'manager__user')
        return Hostel.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'director_profile') and not user.is_superuser:
            raise PermissionDenied("Only Directors or Superusers can create hostels.")

        institute_from_payload = serializer.validated_data.get('institute')
        
        if hasattr(user, 'director_profile'):
            if institute_from_payload != user.director_profile.institute:
                raise ValidationError({"institute": "You can only create hostels for your assigned institute."})
            serializer.save(director=user.director_profile, institute=user.director_profile.institute)
        elif user.is_superuser:
            if not institute_from_payload:
                 raise ValidationError({"institute": "Institute is required for superuser."})
            serializer.save() 
        else:
            raise PermissionDenied("Action not allowed.")


    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class DirectorHostelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hostel.objects.all().select_related('institute', 'director', 'manager__user')
    serializer_class = HostelSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if not user.is_superuser and hasattr(user, 'director_profile'):
            if obj.institute != user.director_profile.institute:
                raise PermissionDenied("You do not have permission to manage this hostel.")
        elif not user.is_superuser: 
            raise PermissionDenied("You do not have permission to manage this hostel.")
        return obj

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context