"""
Board views for listing/creating boards and retrieving/updating/deleting a single board.

Conventions:
- Uses DRF generic class-based views for standard CRUD patterns.
- Enforces authentication on all endpoints.
- Applies object-level permissions to restrict access based on ownership/membership.
- Chooses serializers by action to separate write, list, and detailed read concerns.
"""
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwnerOrMember
from app_board.models import Board
from app_task.models import Task
from .serializers import BoardSerializer, BoardUpdateSerializer, BoardRetrieveSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse

@extend_schema(
    description="List all boards visible to the authenticated user or create a new board.",
    request=BoardSerializer,
    responses={
        200: OpenApiResponse(response=BoardSerializer, description="List of boards retrieved successfully."),
        201: OpenApiResponse(response=BoardSerializer, description="Board created successfully."),
        400: OpenApiResponse(description="Invalid input data."),
        401: OpenApiResponse(description="Authentication credentials were not provided or are invalid."),
    }
)
class BoardList(generics.ListCreateAPIView):
    """
    List boards visible to the current user or create a new board.

    GET:
        Returns boards the user owns or is a member of (admins see all).

    POST:
        Creates a new board.
        Behavior:
            - Sets the authenticated user as the owner.
            - Ensures the owner is included in members.
        Request body:
            - title (str, required)
            - members (list[int], optional) — user IDs; owner is appended automatically
        Response:
            201 with serialized board summary (BoardSerializer).
    """
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        set current logged user as owner and first member, if no members are set
        """
        members = serializer.validated_data.get('members', [])
        members.append(self.request.user.id) 
        serializer.save(owner_id=self.request.user, members=members)

    def get_queryset(self):
        """
        Filter boards by current logged user,
        Does User own board or is he member of board?
        """
        user = self.request.user
        if user.is_superuser:
            return Board.objects.all()
        
        owned_boards = Board.objects.filter(owner_id=user)
        member_boards = Board.objects.filter(members=user)
        # Union of both queries, no duplicates
        return owned_boards.union(member_boards) 


@extend_schema(
    description="Retrieve, update, or delete a specific board (requires ownership or membership).",
    request=BoardUpdateSerializer,
    responses={
        200: OpenApiResponse(response=BoardRetrieveSerializer, description="Board details retrieved or updated successfully."),
        204: OpenApiResponse(description="Board deleted successfully."),
        400: OpenApiResponse(description="Invalid request data."),
        401: OpenApiResponse(description="Authentication required."),
        403: OpenApiResponse(description="Permission denied (not owner or member)."),
        404: OpenApiResponse(description="Board not found."),
    }
)
class BoardDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a board.

    GET:
        Returns a detailed board representation with nested members and tasks
        (BoardRetrieveSerializer).

    PUT/PATCH:
        Updates board title and membership (BoardUpdateSerializer).
        Additional behavior:
            - If users are removed from board members, any tasks where they
              served as assignee or reviewer are unassigned (set to None / Null).

    DELETE:
        Deletes the board. Requires owner or admin (enforced via IsOwnerOrMember).

    Permissions:
        - Authenticated users only.
        - Object-level: IsOwnerOrMember (owner, member, or admin; delete restricted
          to owner/admin).
    """
    queryset = Board.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrMember]

    def get_serializer_class(self):
        """
        Choose serializer based on HTTP method:
            - PUT/PATCH -> BoardUpdateSerializer
            - otherwise -> BoardRetrieveSerializer
        """
        if self.request.method in ['PATCH', 'PUT']:
            return BoardUpdateSerializer
        return BoardRetrieveSerializer # Default => GET
    
    def perform_update(self, serializer):
        """
        Persist updates and reconcile task assignments for removed members.

        Steps:
            1) Capture current members (old state).
            2) Save the board with incoming changes (including members).
            3) Capture updated members (new state).
            4) Compute removed member IDs.
            5) For all tasks on this board where a removed user was assignee or reviewer,
               set those fields to None (unassign).

        Notes:
            - Uses efficient bulk updates for Task to avoid per-instance saves.
        """

        board = self.get_object()

        # Snapshot old members (as IDs)
        old_members = set(board.members.values_list("id", flat=True))

        # Save updates, including potential member changes
        board = serializer.save()  

        # Snapshot new members (as IDs)
        new_members = set(board.members.values_list("id", flat=True))

        # Identify removed users
        removed = old_members - new_members  

        if removed:
            # Unassign removed users from tasks (assignee and/or reviewer)
            Task.objects.filter(board=board, assignee_id__in=removed).update(assignee=None)
            Task.objects.filter(board=board, reviewer_id__in=removed).update(reviewer=None)

