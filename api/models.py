from django.db import models

class PokedexPokemon(models.Model):
    name = models.TextField(default='')
    attack = models.IntegerField(default=0)
    hp = models.IntegerField(default=0)
    defence = models.IntegerField(default=0)
    img = models.TextField(default='', blank=True, null=True)
    weight = models.TextField(default=0)
    height = models.TextField(default=0)
    speed = models.TextField(default=0)

    def __str__(self):
        return self.name