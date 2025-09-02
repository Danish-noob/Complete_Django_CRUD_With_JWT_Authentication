from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.created_by == request.user


class IsAdminOrOwner(permissions.BasePermission):
    """
    Custom permission to allow access to admin users or owners.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role in ['admin', 'owner'] or request.user.is_staff
        return False


class IsManagerOrAbove(permissions.BasePermission):
    """
    Custom permission to allow access to manager, admin, or owner roles.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role in ['manager', 'admin', 'owner'] or request.user.is_staff
        return False


class IsSameOrganization(permissions.BasePermission):
    """
    Custom permission to ensure user can only access data from their organization.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if object has organization attribute
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        
        # Check if object is a user in same organization
        if isinstance(obj, User):
            return obj.organization == request.user.organization
        
        return True


class CanCreateUsers(permissions.BasePermission):
    """
    Permission for creating new users (admin and owner only).
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role in ['admin', 'owner'] or request.user.is_staff
        return False


class CanManageProducts(permissions.BasePermission):
    """
    Permission for managing products (manager and above).
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.method in permissions.SAFE_METHODS:
                return True
            return request.user.role in ['manager', 'admin', 'owner'] or request.user.is_staff
        return False


class CanDeleteProducts(permissions.BasePermission):
    """
    Permission for deleting products (admin and owner only).
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            if request.method != 'DELETE':
                return True
            return request.user.role in ['admin', 'owner'] or request.user.is_staff
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Others can only read.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        elif isinstance(obj, User):
            return obj == request.user
        
        return False


class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission for organization owners only.
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role == 'owner' or request.user.is_staff
        return False


class CanViewAnalytics(permissions.BasePermission):
    """
    Permission for viewing analytics (admin and owner).
    """
    
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.role in ['admin', 'owner'] or request.user.is_staff
        return False


class IsAPIKeyOwner(permissions.BasePermission):
    """
    Permission for API key management.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user is from same organization and has appropriate role
        return (obj.organization == request.user.organization and 
                request.user.role in ['admin', 'owner'])
