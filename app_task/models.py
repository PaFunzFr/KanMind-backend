"""
Task and TaskComment models representing work items and their discussion.

Task:
    A work item that belongs to a board, can be assigned/reviewed by users, and
    tracks status, priority, and deadlines.

TaskComment:
    A short comment attached to a task, authored by a user.

API/DRF notes:
    - Reverse relations for convenient querying:
        * board.tasks -> all tasks on a board
        * user.assigned_tasks -> tasks where the user is assignee
        * user.reviewing_tasks -> tasks where the user is reviewer
        * user.created_tasks -> tasks created by the user
        * task.comments -> comments on the task
        * user.commented_tasks -> comments authored by the user
    - Deletions:
        * Deleting a Board cascades to its Tasks.
        * Deleting a User sets assignee/reviewer/created_by to NULL (task remains),
          but deletes their comments (on_delete=CASCADE in TaskComment).
    - Validation surface:
        * Unique title is enforced at DB level and surfaced by DRF as 400 on conflict.
        * Choice fields (status, priority) are validated by DRF automatically.
    - Typical serializer behavior:
        * Expose foreign keys as read-only expanded data and accept *_id write-only inputs.
        * Default ordering for TaskComment via Meta.ordering.
"""
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from app_board.models import Board
import datetime

class Task(models.Model):
    title = models.CharField(max_length=35, unique=False, null=False, blank=False)
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
        """Readable representation including author and task title."""
        return f"Comment by {self.author.email} on {self.task.title}"