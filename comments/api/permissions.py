from rest_framework.permissions import BasePermission 


class IsObjectOwner(BasePermission):
    """
    The permission is responsible to check of obj.user == request.user
    - action detail=False, only check has_permission
    - action detail=True, check both has_permission and has_object_permission
    When error occur, show IsObjectOwner.message
    """

    message = "You don't have permission to access the object"

    def has_permission(self, request, view):
        return True 
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user