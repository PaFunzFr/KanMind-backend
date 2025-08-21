from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from app_board.models import Board
import datetime

class Task(models.Model):
    title = models.CharField(max_length=35, unique=True, null=False, blank=False)
    description = models.TextField(max_length=250, null=False, blank=False)
    board = models.ForeignKey(Board, related_name='tasks', on_delete=models.CASCADE)
    assignee = models.ForeignKey(
        User,
        related_name='assigned_tasks',
        on_delete=models.SET_NULL,  # User deleted -> field to null
        null=True,
        blank=True
    )
    reviewer = models.ForeignKey(
        User,
        related_name='reviewing_tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        related_name='created_tasks',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    status = models.CharField(max_length=20, choices=[
        # (value, label)
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Reviewing'),
        ('done', 'Done'),
    ], default='to-do')
    priority = models.CharField(max_length=20, choices=[
        # (value, label)
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default ='medium')
    due_date = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class TaskComment(models.Model):
    author = models.ForeignKey(User, related_name='commented_tasks', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    content = models.CharField(max_length=250, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.email} on {self.task.title}"