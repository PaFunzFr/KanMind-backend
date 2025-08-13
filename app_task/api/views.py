from rest_framework import generics
from app_task.models import Task
from .serializers import TaskSerializer

class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer