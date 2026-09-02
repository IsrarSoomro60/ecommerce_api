from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrStaffOrReadOnly(BasePermission):
    """
    Anyone can read (GET/HEAD/OPTIONS).
    Only users with role 'admin' or 'staff' can write (POST/PUT/PATCH/DELETE).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['admin', 'staff']
        )