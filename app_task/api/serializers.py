from rest_framework import serializers
from app_task.models import Task
from app_board.models import Board
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
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
    url = serializers.HyperlinkedIdentityField(view_name='task-detail', lookup_field='pk')
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
                'id',
                'url',
                'title',
                'description',
                'status',
                'priority',
                'assignee',
                'reviewer',
                'due_date',
                'comments_count',
                'assignee_id',
                'reviewer_id',
                'board',
                ]
        read_only_fields = ['id', 'assignee', 'reviewer', 'comments_count']

    def get_comments_count(self, obj):
        """
        Displays the number of task for a given task.
        """
        return obj.comments.count()
    