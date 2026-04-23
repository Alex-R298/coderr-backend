from rest_framework.permissions import BasePermission, SAFE_METHODS

from profiles_app.models import UserProfile


class IsCustomerForCreate(BasePermission):
    """Only authenticated customer users may create reviews."""

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return UserProfile.objects.filter(
            user=request.user, type='customer'
        ).exists()


class IsReviewerOrReadOnly(BasePermission):
    """Only the reviewer may edit or delete their review."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.reviewer == request.user
