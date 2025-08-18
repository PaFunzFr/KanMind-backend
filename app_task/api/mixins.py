from rest_framework import serializers
class CommentCountMixin:
    def get_comments_count(self, obj):
        return obj.comments.count()
    
class TaskMemberValidationMixin:
    def validate(self, data):
        """
        Ensure that assignee and reviewer are valid board members.

        This validation runs on both create and update operations:
        - On CREATE (self.instance is None), values come directly from `data`.
        - On UPDATE, clients may send only a subset of fields (e.g. just "status").
          In that case, missing fields (like assignee, reviewer, or board) are taken
          from the existing instance using `getattr(self.instance, ...)`.

        Logic:
        - If an assignee is set, check that they belong to the given board.
        - If a reviewer is set, check that they belong to the given board.
        - Raise ValidationError if either user is not a member of the board.

        Returns:
            data (dict): The validated data dictionary.
        """
        assignee = data.get('assignee') or getattr(self.instance, 'assignee', None)
        reviewer = data.get('reviewer') or getattr(self.instance, 'reviewer', None)
        board = data.get('board') or getattr(self.instance, 'board', None)

        if board:
            if assignee is not None and (assignee not in board.members.all()):
                raise serializers.ValidationError("Assignee must be a member of the board")

            if reviewer is not None and (reviewer not in board.members.all()):
                raise serializers.ValidationError("Reviewer must be a member of the board")

        return data
