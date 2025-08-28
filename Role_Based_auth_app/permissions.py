from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
   
     def has_permission(self, request, view):
    
        if not request.user or not request.user.is_authenticated:
            return False

    
        return request.user.role == 'admin'


class IsUserRole(BasePermission):
    def has_permission(self, request, view):
        token = getattr(request, "auth", None)
        if token is None:
            return False

        role = token.get("role", None)
        return role == "user"
    
    