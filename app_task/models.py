from django.db import models
from app_auth.models import User
from app_board.models import Board

class Task(models.Model):
    title = models.CharField(max_length=25, unique=True, null=False, blank=False)
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks')
    reviewed_by = models.ForeignKey(User, related_name='reviewing_tasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], default='todo')
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title