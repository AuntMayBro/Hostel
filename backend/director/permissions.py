from rest_framework.permissions import BasePermission, SAFE_METHODS
from backend.hostel import permissions

class IsDirectorOrReadOnly(BasePermission):
    """
    Only allow directors to create, update, or delete.
    Others can only read (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if hasattr(request.user, 'director'):
            director = request.user.director
            # Example: ensure only editing their own institute's data
            institute_id = view.kwargs.get('institute_id')
            return str(director.institute.id) == str(institute_id)

        return False

class IsDirectorOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow directors to edit their own data.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # So we'll always allow GET, HEAD, or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner (director) of the object.
        return obj.user == request.user