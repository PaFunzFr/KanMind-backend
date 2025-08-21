"""
Board model representing a collaborative workspace that groups tasks and users.

Fields:
    - title (CharField, unique, required):
        Short, human-readable name of the board. Must be unique across all boards.
    - members (ManyToMany[User], related_name='member_in_boards'):
        Users who are members of the board and can access its content.
    - owner_id (ForeignKey[User], related_name='boards', on_delete=CASCADE):
        The user who owns the board. Deleting the owner deletes the board.
        Note: Field name 'owner_id' is a ForeignKey to User; in code, it returns
        the User instance (not just the raw ID). Consider renaming to 'owner'
        for conventional clarity.
    - created_at (DateTimeField, auto_now_add=True):
        Timestamp when the board was created.

Conventions and API notes (DRF):
    - Reverse relations:
        * user.member_in_boards -> all boards where the user is a member.
        * user.boards -> all boards the user owns.
    - Permissions:
        Typically, only the owner or admins can delete a board; members can read
        and may update depending on your permission classes (see IsOwnerOrMember).
    - Serialization:
        Expose 'owner' or 'owner_id' as read-only in serializers and set it
        automatically in the view’s perform_create().
    - Validation:
        The unique title is enforced at the DB/ORM level; DRF will surface a 400
        with a clear error when violated.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Board(models.Model):
    title = models.CharField(max_length=25, unique=True, null=False, blank=False)
    members = models.ManyToManyField(User, related_name='member_in_boards')
    owner_id = models.ForeignKey(User, related_name='boards', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the board title for admin and shell readability."""
        return self.title