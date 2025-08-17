from rest_framework import serializers
from app_auth.api.serializers import UserInfoSerializer
from app_task.api.serializers import TaskRetrieveSerializer
from app_board.models import Board
from django.contrib.auth import get_user_model

User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
    """ Fields Write Only """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )

    """ Fields Read Only """
    # title: unique=True in model => DRF handles validation automatically
    # owner_id: set automatically in perform_create() => read-only here
    # created_at: auto_now_add=True in model => read-only
    url = serializers.HyperlinkedIdentityField(view_name='board-detail', lookup_field='pk')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = ['id','url','title','member_count','ticket_count','tasks_to_do_count',
                  'tasks_high_prio_count','owner_id','members'
                ]
        read_only_fields = ['id', 'created_at', 'owner']
        write_only_fields = ['members']

    def get_member_count(self, obj):
        """
        Displays the number of members for a given board.
        """
        return obj.members.count()
    
    def get_ticket_count(self, obj):
        return obj.tasks.count()
    
    def get_tasks_to_do_count(self, obj):
        tasks = obj.tasks.filter(status='todo').count()
        return tasks
    
    def get_tasks_high_prio_count(self, obj):
        tasks = obj.tasks.filter(priority='high').count()
        return tasks

class BoardRetrieveSerializer(serializers.ModelSerializer):
    members = UserInfoSerializer(many=True, read_only=True)
    tasks = TaskRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    owner_data = UserInfoSerializer(read_only=True, source='owner')
    members_data = UserInfoSerializer(many=True, read_only=True, source='members')
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False,
        write_only=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members_data', 'members']
        read_only_fields = ['id', 'owner_data', "members_data"]