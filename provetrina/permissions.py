from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsProfileOwnerOrReadOnlyPublicProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        profile = obj
        return bool(
            profile.owner_id == request.user.pk
            or (request.method in SAFE_METHODS and profile.public)
        )


class IsSectionOwnerOrReadOnlyPublicProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        section = obj
        return bool(
            section.profile_id == request.user.pk
            or (request.method in SAFE_METHODS and section.profile.public)
        )
