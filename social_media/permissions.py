from rest_framework.permissions import BasePermission
from .models import Profile


class IsTwitterOwner(BasePermission):
    message = "You are not allowed to view this object. only owners of this object, can view it."

    def has_object_permission(self, request, view, obj):
        return obj.profile == Profile.get_profile_for_user(request.user)


class IsReportTwitteOwner(BasePermission):
    message = "You are not allowed to view this object. only owners of this object, can view it."

    def has_object_permission(self, request, view, obj):
        return obj.reporter == Profile.get_profile_for_user(request.user)