from rest_framework import permissions
from app_board.models import Board
from app_task.models import Task

class IsBoardMember(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return Board.objects.filter(pk=request.data.get("board"),members=request.user).exists()
        else:
            return True

class IsCreatorOrBoardMember(permissions.BasePermission):
    """
    Permission if user part of members or owner
    """

    def has_object_permission(self, request, view, obj):
        """ Defined user roles """
        user = request.user
        is_member = obj.board.members.filter(pk=user.pk).exists()
        is_creator = (obj.created_by is not None) and (user == obj.created_by)
        is_owner = request.user == obj.board.owner_id
        is_admin = user.is_superuser

        if request.method == "DELETE":
            """ only owner or admin can delete """
            return is_creator or is_owner or is_admin
        else:
            """ only member, owner or admin can update """
            return is_member or is_creator or is_owner or is_admin
        
class IsBoardMemberOfTask(permissions.BasePermission):
    def has_permission(self, request, view):
        return Task.objects.filter(pk=request.data.get("task"),board__members=request.user).exists()
