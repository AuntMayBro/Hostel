from rest_framework.exceptions import ValidationError
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Director
from .serializers import DirectorRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
from rest_framework import generics
from .models import Institute, Course, Branch
from .serializers import CourseSerializer, BranchSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import *

# Create your Views here

class DirectorCreateView(generics.CreateAPIView):
    """
    Registers a new director with associated institute and user.
    Returns JWT token upon successful registration.
    """
    serializer_class = DirectorRegistrationSerializer
    permission_classes = [permissions.AllowAny] 

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        director = serializer.save()

        # Assuming director.user is the User instance
        user = director.user

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response(
            {
                "message": "Director registered successfully",
                "access": access_token,
                "refresh": refresh_token,
            },
            status=status.HTTP_201_CREATED
        )

class DirectorDetailView(generics.RetrieveAPIView):
    """
    Retrieves director details by ID (or restrict to request.user).
    """
    queryset = Director.objects.all()
    serializer_class = DirectorRegistrationSerializer
    permission_classes = [IsAuthenticated, IsDirectorOrReadOnly]
    lookup_field = 'pk'


class DirectorUpdateView(generics.UpdateAPIView):
    """
    Updates director details by ID (or restrict to request.user).
    """
    queryset = Director.objects.all()
    serializer_class = DirectorRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'



'''
-----------------------------------------------------------------------
            Courses and branches VIEWs
-----------------------------------------------------------------------

'''

class InstituteCourseListCreateView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer
    # permission_classes = [IsAuthenticated, IsDirectorOrReadOnly]

    def get_queryset(self):
        institute_id = self.request.query_params.get('institute_id')

        if institute_id is None:
            raise ValidationError("institute_id is required as a query parameter.")

        return Course.objects.filter(institute__id=institute_id)

    def perform_create(self, serializer):
        institute_id = self.request.query_params.get('institute_id')
        if not institute_id:
            raise ValidationError("Missing 'institute_id' in query parameters.")

        try:
            institute = Institute.objects.get(id=institute_id)
        except Institute.DoesNotExist:
            raise ValidationError("Institute not found.")

        code = serializer.validated_data.get('code')

        if Course.objects.filter(code=code, institute__id=institute_id).exists():
            raise ValidationError(f"Course with code '{code}' already exists for this institute.")

        serializer.save(institute=institute)    

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [IsAuthenticated]

class CourseBranchListCreateView(generics.ListCreateAPIView):
    serializer_class = BranchSerializer
    # permission_classes = [IsAuthenticated, IsDirectorOrReadOnly]

    def get_queryset(self):
        institute_id = self.request.query_params.get('institute_id')

        if institute_id is None:
            raise ValidationError("institute_id is required as a query parameter.")

        return Branch.objects.filter(course__institute_id=institute_id)

    def perform_create(self, serializer):
        institute_id = self.request.query_params.get('institute_id')
        if not institute_id:
            raise ValidationError("Missing 'institute_id' in query parameters.")

        try:
            institute = Institute.objects.get(id=institute_id)
        except Institute.DoesNotExist:
            raise ValidationError("Institute not found.")

        course = serializer.validated_data.get('course')
        code = serializer.validated_data.get('code')

        if course.institute_id != institute.id:
            raise ValidationError("The selected course does not belong to the given institute.")

        if Branch.objects.filter(code=code, course=course).exists():
            raise ValidationError(f"Branch with code '{code}' already exists under this course.")

        serializer.save()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class BranchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]