from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .models import Director
from .serializers import DirectorRegistrationSerializer
from rest_framework_simplejwt.tokens import RefreshToken # type: ignore
# Create your Views here

class DirectorCreateView(generics.CreateAPIView):
    """
    Registers a new director with associated institute and user.
    Returns JWT token upon successful registration.
    """
    serializer_class = DirectorRegistrationSerializer
    permission_classes = [permissions.AllowAny]  # Adjust as needed

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
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'


class DirectorUpdateView(generics.UpdateAPIView):
    """
    Updates director details by ID (or restrict to request.user).
    """
    queryset = Director.objects.all()
    serializer_class = DirectorRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'