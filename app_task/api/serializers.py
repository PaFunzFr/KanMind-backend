from rest_framework import serializers
from app_task.models import Task, TaskComment
from app_board.models import Board
from app_auth.api.serializers import UserInfoSerializer
from django.contrib.auth import get_user_model
from .mixins import CommentCountMixin, TaskMemberValidationMixin

User = get_user_model()


class TaskSerializer(CommentCountMixin, TaskMemberValidationMixin, serializers.ModelSerializer):
    """ Fields Write Only """
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        source='assignee'
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        source='reviewer'
    )
    board = serializers.PrimaryKeyRelatedField(
        queryset=Board.objects.all(),
    )

    """ Fields Read Only """
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
    """ Fields Read Only """
    assignee = UserInfoSerializer(read_only=True)
    reviewer = UserInfoSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'priority', 'assignee',
                  'reviewer', 'due_date', 'comments_count']


class TaskUpdateSerializer(TaskMemberValidationMixin, TaskRetrieveSerializer):
    """ Fields Write Only """
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        source='assignee'
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        source='reviewer'
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assignee', 'reviewer',
                  'reviewer_id', 'assignee_id', 'due_date', 'priority', 'status']
        
class TaskCommentSerializer(serializers.ModelSerializer):
    """ Fields Read Only """
    author = serializers.StringRelatedField()
    class Meta:
        model = TaskComment
        fields = ['id', 'created_at', 'author', 'content']