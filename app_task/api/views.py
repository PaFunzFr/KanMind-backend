from django.forms import ValidationError
from rest_framework import generics
from app_task.models import Task, TaskComment
from rest_framework.permissions import IsAuthenticated
from .permissions import IsCreatorOrBoardMember, IsCommentOwner
from .serializers import TaskSerializer, TaskRetrieveSerializer, TaskUpdateSerializer, TaskCommentSerializer

class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        user = self.request.user
        board = serializer.validated_data.get("board")

        """ not allowed to create tasks if not member of its board """
        if not board or not board.members.filter(pk=user.pk).exists():
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You must be a member of the selected board to create a task.")
    
        """ set current logged user as creator """
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        """ only board members can see task """
        user = self.request.user
        if user.is_superuser:
            return Task.objects.all()
        else:
            return Task.objects.filter(board__members=user)


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsCreatorOrBoardMember]

    def get_serializer_class(self):
        """
        Chosen serializer class depends on the HTTP method.
        """
        if self.request.method in ['PATCH', 'PUT']:
            return TaskUpdateSerializer
        return TaskRetrieveSerializer # Default => GET


class CommentList(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        task_pk = self.kwargs['pk_task']
        is_member = Task.objects.filter(pk=task_pk, board__members=user).exists()
        if not is_member and not user.is_superuser:
            return TaskComment.objects.none()
        return TaskComment.objects.filter(task_id=task_pk).order_by('-created_at')


    def perform_create(self, serializer):
        """Auto set user as author and link to current task"""
        task_pk = self.kwargs['pk_task']
        try:
            task = Task.objects.get(pk=task_pk)
            serializer.save(
                task=task,
                author=self.request.user
            )
        except Task.DoesNotExist:
            raise ValidationError(f"Task with ID {task_pk} not found")


class AssignedTasksList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskRetrieveSerializer

    def get_queryset(self):
        """
        Filter tasks by current logged user and its assigned tasks
        """
        user = self.request.user
        assigned_tasks = Task.objects.filter(assignee=user)
        return assigned_tasks

class ReviewTasksList(generics.ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskRetrieveSerializer

    def get_queryset(self):
        """
        Filter tasks by current logged user and its reviewed tasks
        """
        user = self.request.user
        reviewed_tasks = Task.objects.filter(reviewer=user) 
        return reviewed_tasks

class DeleteComment(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCommentOwner]
    serializer_class = TaskCommentSerializer
    lookup_url_kwarg = 'pk_comment' # set object to delete

    def get_queryset(self):
        return TaskComment.objects.filter(task_id=self.kwargs['pk_task'])