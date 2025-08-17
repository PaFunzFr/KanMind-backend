from django.forms import ValidationError
from rest_framework import generics
from app_task.models import Task, TaskComment
from .serializers import TaskSerializer, TaskRetrieveSerializer, TaskUpdateSerializer, TaskCommentSerializer

class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    def get_serializer_class(self):
        """
        Chosen serializer class depends on the HTTP method.
        """
        if self.request.method in ['PATCH', 'PUT']:
            return TaskUpdateSerializer
        return TaskRetrieveSerializer # Default => GET
    
class CommentList(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer

    def get_queryset(self):
        task_pk = self.kwargs['pk']  # Task-ID from URL
        return TaskComment.objects.filter(task=task_pk)

    def perform_create(self, serializer):
        """Auto set user as author and link to current task"""
        task_pk = self.kwargs['pk']
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