"""
Serializers for Task and TaskComment resources.

Provides:
- TaskSerializer: Create/list serializer with write-only IDs for assignee/reviewer and
  read-only computed comment count and hyperlink.
- TaskRetrieveSerializer: Detailed read-only view with nested user info and comment count.
- TaskUpdateSerializer: Update serializer accepting assignee/reviewer IDs with membership validation.
- TaskCommentSerializer: Read-only serializer for task comments.

Conventions:
- Separate serializers by use case (create/list vs retrieve vs update).
- Use write-only *_id fields to accept user PKs while exposing expanded read-only relations.
- Computed fields (comments_count) via mixin for reuse.
- Membership validation handled in TaskMemberValidationMixin for assignee/reviewer.
"""
from rest_framework import serializers
from app_task.models import Task, TaskComment
from app_board.models import Board
from app_auth.api.serializers import UserInfoSerializer
from django.contrib.auth import get_user_model
from .mixins import CommentCountMixin, TaskMemberValidationMixin

User = get_user_model()


class TaskSerializer(CommentCountMixin, TaskMemberValidationMixin, serializers.ModelSerializer):
    """
    Create/list serializer for tasks with write-only relation IDs and read-only aggregates.

    Write-only inputs:
        - assignee_id (int | null): PK of the assignee user; mapped to 'assignee'.
        - reviewer_id (int | null): PK of the reviewer user; mapped to 'reviewer'.
        - board (int): PK of the board to which the task belongs.

    Read-only outputs:
        - id (int)
        - url (str): Hyperlink to the detail endpoint for this task.
        - assignee (User | null): Exposed as read-only field (see Meta).
        - reviewer (User | null): Exposed as read-only field (see Meta).
        - comments_count (int): Computed count of comments for this task.

    Validation:
        - TaskMemberValidationMixin should ensure assignee/reviewer are members of the task's board.

    Notes:
        - The model enforces valid choices for status/priority if defined there.
        - Ensure request context is provided for HyperlinkedIdentityField.
    """

    # Write-only relationship IDs map to actual FK fields via 'source'
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,  
        source='assignee'
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,  
        source='reviewer'
    )
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(),
    )

    # Read-only fields
    url = serializers.HyperlinkedIdentityField(
        view_name='task-detail',
        lookup_field='pk'
    )
    comments_count = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = ['id','url','title','description','status','priority','assignee',
                  'reviewer','due_date','comments_count','assignee_id','reviewer_id','board',]
        read_only_fields = ['id', 'assignee', 'reviewer', 'comments_count']


class TaskRetrieveSerializer(CommentCountMixin, serializers.ModelSerializer):
    """
    Detailed read-only task representation with nested user info and comment count.

    Fields:
        - id, title, description, status, priority, due_date
        - assignee (UserInfoSerializer | null, read-only)
        - reviewer (UserInfoSerializer | null, read-only)
        - comments_count (int, computed)
        - created_by (User ID or object, depending on model)
        - board (Board ID or object, depending on model/serializer)
    """
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee',
                  'reviewer', 'due_date', 'comments_count', 'created_by', 'board']


class TaskUpdateSerializer(TaskMemberValidationMixin, TaskRetrieveSerializer):
    """
    Update serializer that accepts *_id inputs while exposing expanded read-only relations.

    Write-only inputs:
        - assignee_id (int | null): New assignee PK.
        - reviewer_id (int | null): New reviewer PK.

    Read-only outputs (inherited):
        - assignee, reviewer (expanded via UserInfoSerializer)

    Validation:
        - TaskMemberValidationMixin enforces that the new assignee/reviewer belong to the task's board.
    """
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,  
        source='assignee'
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,  
        source='reviewer'
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'reviewer',
                  'reviewer_id', 'assignee_id', 'due_date', 'priority', 'status']
        
class TaskCommentSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for task comments.

    Fields:
        - id (int)
        - created_at (datetime)
        - author (str): Human-readable user via __str__ of the author.
        - content (str)
    """
    author = serializers.StringRelatedField()
    class Meta:
        model = TaskComment
        fields = ['id', 'created_at', 'author', 'content']