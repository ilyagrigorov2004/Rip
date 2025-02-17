from rest_framework import permissions
from .auth_utils import getUserByToken

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserByToken(request)
        return bool(user and (user.is_staff or user.is_superuser))

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserByToken(request)
        return bool(user and user.is_superuser)
    
class IsAuth(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserByToken(request)
        if (user and user.is_authenticated):
            return True
        else:
            return False
    
class IsAuthOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserByToken(request)
        return bool(user) or request.method in permissions.SAFE_METHODS