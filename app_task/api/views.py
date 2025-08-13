from rest_framework import generics
from app_task.models import Task
from .serializers import TaskSerializer, TaskRetrieveSerializer, TaskUpdateSerializer

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