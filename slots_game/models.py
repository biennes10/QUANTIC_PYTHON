# slots_game/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    balance = models.IntegerField(default=100) # Champ balance initialisé à 100

    def __str__(self):
        return self.username