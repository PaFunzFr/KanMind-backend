"""
Task and comment views implementing list/create, retrieve/update/destroy, and specialty listings.

Conventions:
- Uses DRF generic views for standard CRUD.
- Enforces authentication and object-level permissions where appropriate.
- Selects serializers per action to separate write vs read concerns.
"""
from django.shortcuts import get_object_or_404
from rest_framework import generics
from app_task.models import Task, TaskComment
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCreatorOrBoardMember, IsCommentOwner
from .serializers import TaskSerializer, TaskRetrieveSerializer, TaskUpdateSerializer, TaskCommentSerializer

class TaskList(generics.ListCreateAPIView):
    """
    List tasks visible to the user or create a new task.

    GET:
        - Superusers: all tasks.
        - Regular users: tasks where they are members of the task's board.

    POST:
        - Creates a task for a given board.
        - Requirements:
            * 'board' must be provided in payload.
            * Requesting user must be a member of that board.
        - Side effects:
            * Sets 'created_by' to the current authenticated user.

    Permissions:
        - IsAuthenticated
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Validate board membership before creation and set creator.
        """
        user = self.request.user
        board = serializer.validated_data.get("board")

        if not board or not board.members.filter(pk=user.pk).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You must be a member of the selected board to create a task.")
    
        # Stamp creator
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """
        Restrict visibility to tasks on boards the user belongs to (admins see all).
        """
        user = self.request.user
        if user.is_superuser:
            return Task.objects.all()
        else:
            return Task.objects.filter(board__members=user)


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a single task.

    GET:
        - Returns a detailed representation (TaskRetrieveSerializer).

    PUT/PATCH:
        - Updates task fields (TaskUpdateSerializer).
        - Validation ensures assignee/reviewer belong to the task's board.

    DELETE:
        - Allowed if the user is the creator, board owner, or admin (via IsCreatorOrBoardMember).

    Permissions:
        - IsAuthenticated
        - IsCreatorOrBoardMember (object-level)
    """
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsCreatorOrBoardMember]

    def get_serializer_class(self):
        """
        Choose serializer based on HTTP method:
            - PUT/PATCH -> TaskUpdateSerializer
            - otherwise -> TaskRetrieveSerializer
        """
        if self.request.method in ['PATCH', 'PUT']:
            return TaskUpdateSerializer
        return TaskRetrieveSerializer # Default => GET


class CommentList(generics.ListCreateAPIView):
    """
    List or create comments for a specific task.

    GET:
        - Returns comments for task <pk_task> if the user is a member of the task's board
          or is a superuser; otherwise returns an empty list.

    POST:
        - Creates a new comment for task <pk_task>.
        - Automatically sets 'author' to the current user and links to the task.

    Permissions:
        - IsAuthenticated
    """
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Restrict comment visibility to members of the task's board or admins.
        """
        user = self.request.user
        task_pk = self.kwargs['pk_task']
        is_member = Task.objects.filter(pk=task_pk, board__members=user).exists()
        if not is_member and not user.is_superuser:
            return TaskComment.objects.none()
        return TaskComment.objects.filter(task_id=task_pk).order_by('-created_at')


    def perform_create(self, serializer):
        """
        Auto-assign the current user as author and associate with the URL task.
        """
        task_pk = self.kwargs['pk_task']
        task = get_object_or_404(Task, pk=task_pk)

        user = self.request.user
        is_member = task.board.members.filter(pk=user.pk).exists()
        if not (is_member or user.is_superuser):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You are not allowed to comment on this task.")

        serializer.save(task=task, author=self.request.user)


class AssignedTasksList(generics.ListAPIView):
    """
    List tasks assigned to the current user.

    GET:
        - Returns tasks where 'assignee' equals the current user.
    """
    queryset = Task.objects.all()
    serializer_class = TaskRetrieveSerializer

    def get_queryset(self):
        """
        Filter tasks by current authenticated user and his assigned tasks
        """
        user = self.request.user
        assigned_tasks = Task.objects.filter(assignee=user)
        return assigned_tasks

class ReviewTasksList(generics.ListAPIView):
    """
    List tasks the current user is reviewing.

    GET:
        - Returns tasks where 'reviewer' equals the current user.
    """
    queryset = Task.objects.all()
    serializer_class = TaskRetrieveSerializer

    def get_queryset(self):
        """
        Filter tasks by current authenticated user and his reviewed tasks
        """
        user = self.request.user
        reviewed_tasks = Task.objects.filter(reviewer=user) 
        return reviewed_tasks

class DeleteComment(generics.RetrieveDestroyAPIView):
    """
    Retrieve or delete a specific comment of a specific task.

    GET:
        - Retrieve comment <pk_comment> for task <pk_task>.

    DELETE:
        - Allowed only for the comment's author or admins (IsCommentOwner).

    Permissions:
        - IsAuthenticated
        - IsCommentOwner (object-level)

    Lookup:
        - Uses 'pk_comment' from the URL to identify the comment instance.
        - Queryset is constrained to comments of task <pk_task>.
    """
    permission_classes = [IsAuthenticated, IsCommentOwner]
    serializer_class = TaskCommentSerializer
    lookup_url_kwarg = 'pk_comment' # set object to delete

    def get_queryset(self):
        """
        Restrict deletions/lookups to comments under the target task.
        """
        return TaskComment.objects.filter(task_id=self.kwargs['pk_task'])