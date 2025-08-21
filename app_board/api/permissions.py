"""
Custom DRF permission classes for ownership and membership checks.

Provides:
- IsOwner: Grants access only to the object owner.
- IsOwnerOrMember: Grants access to owner, members, or admin, with stricter rules for DELETE.

Usage:
- Apply on viewsets or views via permission_classes.
- Assumes the target object exposes:
    - owner_id (User): owner reference (note: typically 'owner', ensure equality works)
    - members (RelatedManager): relation with Users supporting .filter(pk=...).exists()
"""
from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Allows access only to the owner of the object.

    Behavior:
        - has_object_permission returns True if the authenticated user matches the object's owner.

    Notes:
        - Ensure that 'obj.owner_id' is a user instance or comparable to request.user.
          If your model uses 'owner' (FK to User), prefer comparing 'request.user == obj.owner'.
    """
    def has_object_permission(self, request, view, obj):
        is_owner = bool(request.user) and request.user == obj.owner_id
        return is_owner
    
class IsOwnerOrMember(permissions.BasePermission):
    """
    Allows access to the owner, members, or admins.

    Behavior:
        - DELETE: restricted to owner or superuser (admin).
        - Other methods (GET/HEAD/OPTIONS/PUT/PATCH): allowed for members, owner, or admin.

    Assumptions:
        - obj.members is a relation to User supporting membership queries.
        - obj.owner_id references the owner (see note below).

    Notes:
        - If your model defines 'owner' (FK to User), compare with 'obj.owner' not 'obj.owner_id'.
        - Superusers bypass membership/ownership checks.
    """

    def has_object_permission(self, request, view, obj):
        """ Defined user roles """
        is_member = bool(request.user) and obj.members.filter(pk=request.user.pk).exists()
        is_owner = bool(request.user) and request.user == obj.owner_id
        is_admin = request.user.is_superuser

        if request.method == "DELETE":
            """ only owner or admin can delete """
            return is_owner or is_admin
        else:
            """ only member, owner or admin can update, read"""
            return is_member or is_owner or is_admin