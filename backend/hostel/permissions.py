from rest_framework.permissions import BasePermission
from hostel.models import Hostel
from rest_framework.permissions import IsAuthenticated

class IsDirectorOrManagerOfHostel(BasePermission):
    """
    Only allow Directors or Managers of the specific hostel to modify room data.
    """
    def has_permission(self, request, view):
        user = request.user
        return hasattr(user, 'director') or hasattr(user, 'hostelmanager')

    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(user, 'director'):
            return obj.hostel.director == user.director
        if hasattr(user, 'hostelmanager'):
            return obj.hostel.manager == user.hostelmanager
        return False


class IsDirector(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'director')


class IsStudent(IsAuthenticated):
    """
    Allows access only to authenticated students.
    Assumes a 'student_profile' OneToOneField on the User model.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view) and hasattr(request.user, 'student_profile')

class IsDirectorOrAdmin(IsAuthenticated):
    """
    Allows access only to authenticated Directors or staff/superusers.
    Assumes a 'director_profile' OneToOneField on the User model.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view) and \
               (request.user.is_staff or request.user.is_superuser or hasattr(request.user, 'director_profile'))

class IsOwnerOrDirectorOrAdmin(IsAuthenticated):
    """
    Allows object access to the owner of the application, or to Directors/Admins.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser or hasattr(request.user, 'director_profile'):
            return True
        return obj.student.user == request.user
