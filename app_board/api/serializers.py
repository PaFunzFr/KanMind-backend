"""
Serializers for Board resources: creation/listing summary, detailed retrieval, and updates.

Provides:
- BoardSerializer: Write members by IDs; read a summarized board with counts and URL.
- BoardRetrieveSerializer: Read-only detailed board with nested members and tasks.
- BoardUpdateSerializer: Update title/members while exposing read-only owner/members info.

Conventions:
- Separate serializers per use case (list/create vs retrieve vs update).
- Write-only relationship inputs (members) to avoid mixing IDs with expanded data.
- Read-only computed fields for aggregated counts.
"""
from rest_framework import serializers
from app_auth.api.serializers import UserInfoSerializer
from app_task.api.serializers import TaskRetrieveSerializer
from app_board.models import Board
from django.contrib.auth import get_user_model

User = get_user_model()

class BoardSerializer(serializers.ModelSerializer):
    """
    Create/list serializer with hyperlinked URL and aggregate counters.

    Write-only fields:
        - members (list[int], optional): Primary keys of users to add as members.

    Read-only fields:
        - id (int): Board primary key.
        - url (str): Canonical URL for this board (HyperlinkedIdentityField).
        - title (str): Board title; uniqueness enforced by the model.
        - owner_id (int): Set automatically (e.g., in view's perform_create()).
        - created_at (datetime): Managed by the model (auto_now_add=True).
        - member_count (int): Number of users in members relation.
        - ticket_count (int): Number of tasks related to the board.
        - tasks_to_do_count (int): Count of tasks with status='todo'.
        - tasks_high_prio_count (int): Count of tasks with priority='high'.

    Notes:
        - DRF will validate 'members' IDs against the User queryset.
        - Ensure the view provides request context for hyperlink generation.
    """

    # Fields (write-only): supply member IDs on create/update without expanding them
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )
    
    # Fields (read-only):
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
        read_only_fields = ['id', 'created_at', 'owner_id']
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
    """
    Detailed read-only representation of a board with nested relations.

    Fields:
        id (int)
        title (str)
        owner_id (int)
        members (list[UserInfoSerializer], read-only)
        tasks (list[TaskRetrieveSerializer], read-only)

    Use cases:
        - Retrieve endpoints that need full member and task details.
    """
    members = UserInfoSerializer(many=True, read_only=True)
    tasks = TaskRetrieveSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']


class BoardUpdateSerializer(serializers.ModelSerializer):
    """
    Update serializer that accepts member IDs but returns expanded user info.

    Read-only projections:
        - owner_data: Expanded owner info (mapped from 'owner_id').
        - members_data: Expanded list of members (mapped from 'members').

    Write-only input:
        - members (list[int], optional): Primary keys of users to set/modify membership.

    Fields:
        id (int, read-only)
        title (str)
        owner_data (UserInfoSerializer, read-only)
        members_data (list[UserInfoSerializer], read-only)
        members (list[int], write-only)

    Notes:
        - Ensure the view handles setting many-to-many members when 'members' is provided.
    """
    owner_data = UserInfoSerializer(read_only=True, source='owner_id')
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