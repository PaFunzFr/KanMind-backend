from django.db import models

class Board(models.Model):
    title = models.CharField(max_length=25, unique=True, null=False, blank=False)
    