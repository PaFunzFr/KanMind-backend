from rest_framework import serializers
from app_board.models import Board
from django.contrib.auth import get_user_model

User = get_user_model()

class BoardMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','full_name', 'email']

class BoardSerializer(serializers.ModelSerializer):
    """ Fields Write Only """
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )

    """ Fields Read Only """
    url = serializers.HyperlinkedIdentityField(view_name='board-detail', lookup_field='pk')
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
                'id',
                'url',
                'title',
                'member_count',
                'ticket_count',
                'tasks_to_do_count',
                'tasks_high_prio_count',
                'owner_id',
                'members'
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


    # """Override the default update method to handle nested data"""
    # def update(self, instance, validated_data):
    #     members_to_add = validated_data.pop('member_ids', None) # get member_ids from the validated data

    #     """Update the board with the provided data."""
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()

    #     """If there are new members, update the board"""
    #     if members_to_add is not None:
    #         instance.members.set(members_to_add)

    #     return instance

    # def create(self, validated_data):
    #     members_to_add = validated_data.pop('member_ids', None)
    #     board = Board.objects.create(**validated_data)

    #     if members_to_add:
    #         board.members.set(members_to_add)

    #     return board
    

class BoardRetrieveSerializer(serializers.ModelSerializer):
    members = BoardMemberSerializer(many=True, read_only=True)
    owner_data = BoardMemberSerializer(read_only=True, source='owner_id')

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_data', 'members']



class BoardUpdateSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=User.objects.all(),
        required=False
    )
    class Meta:
        model = Board
        fields = ['title', 'members']