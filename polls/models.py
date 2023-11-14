from django.db import models
from datetime import date
import datetime
import uuid

class Pokemon(models.Model):
    name = models.TextField(default="")
    pokemon_id = models.IntegerField(default=1) # id в покедексе
    img = models.TextField(default="")
    weight = models.TextField(default=0)
    height = models.TextField(default=0)
    # Это текущие статы покемона, не изначальные
    attack = models.IntegerField(default=0)
    hp = models.IntegerField(default=0)
    defence = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
class FightRoom(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    your_pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name="your_pokemon")
    enemy_pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE, related_name="enemy_pokemon")
    game_ended = models.BooleanField(default=False)
    you_win = models.BooleanField(default=False)
    rounds = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    logs = models.TextField(default='')

    def __str__(self):
        return "{} VS {}".format(self.your_pokemon.name, self.enemy_pokemon.name)