from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrAdminUserReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            obj == request.user
            or (request.user.is_staff and request.method in SAFE_METHODS)
        )
