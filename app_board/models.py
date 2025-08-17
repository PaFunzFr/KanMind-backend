from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Board(models.Model):
    title = models.CharField(max_length=25, unique=True, null=False, blank=False)
    members = models.ManyToManyField(User, related_name='member_in_boards')
    owner = models.ForeignKey(User, related_name='boards', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title