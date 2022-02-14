from rest_framework import permissions

# API for Restricting Creating Access to Admin
class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self,request,view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff 
    
# API for Restricting Modification of Reviews
class ReviewUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self,request,view, object):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.is_staff or request.user == object.review_user)