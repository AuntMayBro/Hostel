from rest_framework.permissions import BasePermission, SAFE_METHODS

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
