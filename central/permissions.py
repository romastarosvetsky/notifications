from rest_framework.permissions import BasePermission


class NotificationOwnerManageOrReadOnly(BasePermission):

    SAFE_METHODS = ['GET', ]

    def has_object_permission(self, request, view, obj):
        if request.method in self.SAFE_METHODS or \
                    request.user and request.user.is_authenticated and obj.owner == request.user:
            return True
        return False
