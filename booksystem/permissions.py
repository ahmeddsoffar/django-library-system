from rest_framework.permissions import BasePermission , SAFE_METHODS

## idea can the this user access this view or not

class IsStaffOrReadOnly(BasePermission):

    def has_permission(self, request,view):
        # Allow read-only access for non-staff users   Allow write access only for staff users
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff) ## see if there is user with the req and if he is staff


class IsOwnerOrStaff(BasePermission): ## staff see all borrowed history while users only see their own
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.member.user_id == request.user.id