from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsCustomerUser(BasePermission):
    """Only customers may create orders."""

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
        if not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        return profile is not None and profile.type == 'customer'


class IsBusinessUserForPatch(BasePermission):
    """Only the business user associated with the order may update status."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return request.user.is_staff
        if request.method in ('PATCH', 'PUT'):
            return obj.business_user == request.user
        return False
