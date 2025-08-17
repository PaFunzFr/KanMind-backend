from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Permission if user is object owner
    """
    def has_object_permission(self, request, view, obj):
        is_owner = bool(request.user) and request.user == obj.owner
        return is_owner
    
class IsOwnerOrMember(permissions.BasePermission):
    """
    Permission if user part of members or owner
    """

    def has_object_permission(self, request, view, obj):
        """ Defined user roles """
        is_member = bool(request.user) and request.user in obj.members.all()
        is_owner = bool(request.user) and request.user == obj.owner
        is_admin = request.user.is_superuser

        if request.method == "DELETE":
            """ only owner or admin can delete """
            return is_owner or is_admin
        else:
            """ only member, owner or admin can update """
            return is_member or is_owner or is_admin