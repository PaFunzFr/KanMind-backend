"""
Custom DRF permission classes for boards, tasks, and comments.

Provides:
- IsBoardMember: Gate POST requests to ensure the requester is a member of the target board.
- IsCreatorOrBoardMember: Object-level checks for creator, board owner, members, and admins.
- IsBoardMemberOfTask: Gate actions referencing a task to members of the task's board.
- IsCommentOwner: Object-level check allowing comment author or admins.

General notes:
- Assumes related models expose:
    - Task.board (FK to Board), Task.created_by (FK to User)
    - Board.members (M2M to User), Board.owner_id (FK to User)
    - Comment.author (FK to User)
- Superusers are treated as admins and generally bypass restrictions where noted.
"""
from rest_framework import permissions
from app_board.models import Board
from app_task.models import Task

class IsBoardMember(permissions.BasePermission):
    """
    Allow a request only if the user is a member of the referenced board (for POST).

    Behavior:
        - POST: Requires 'board' (ID) in request.data and membership in that board.
        - Other methods: Allowed (object-level permissions may still apply upstream).

    Returns:
        True if permitted, False otherwise.
    """

    def has_permission(self, request, view):
        if request.method == "POST":
            return Board.objects.filter(pk=request.data.get("board"),members=request.user).exists()
        else:
            return True

class IsCreatorOrBoardMember(permissions.BasePermission):
    """
    Object-level permission for items tied to a board (e.g., Task, Comment-like entities).

    Roles:
        - Creator: The user who created the object (obj.created_by).
        - Owner:   The board owner (obj.board.owner_id).
        - Member:  Any user in obj.board.members.
        - Admin:   Superuser (request.user.is_superuser).

    Behavior:
        - DELETE: Allowed for creator, owner, or admin.
        - Other methods (GET/PUT/PATCH/HEAD/OPTIONS): Allowed for member, creator, owner, or admin.

    Returns:
        True if the user satisfies the role conditions, False otherwise.
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
    """
    Allow requests that reference a task only if the user is a member of the task's board.

    Expectation:
        - The request body includes 'task' (task ID).

    Returns:
        True if the user belongs to Task.board.members for the provided task ID.
    """
    def has_permission(self, request, view):
        return Task.objects.filter(pk=request.data.get("task"),board__members=request.user).exists()

class IsCommentOwner(permissions.BasePermission):
    """
    Allow object access only to the comment author or admins.

    Behavior:
        - Grants permission if request.user is the comment's author or a superuser.

    Returns:
        True if user is author or admin, False otherwise.
    """
    def has_object_permission(self, request, view, obj):
        is_user = request.user
        is_author = obj.author
        is_admin = is_user.is_superuser
        if (is_user == is_author) or is_admin:
            return True
        else:
            return False