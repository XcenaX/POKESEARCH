import os, sys, time
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','area.settings')
django.setup()

from api.models import PokedexPokemon
from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup as BS
import time
from django.utils import timezone
from polls.game import fetch_certain_pokemon

try:
    i = 680
    while(True):
        pokemon = fetch_certain_pokemon(i)
        new_pokemon = PokedexPokemon.objects.create(
            name=pokemon['name'],
            attack=pokemon['attack'],
            hp=pokemon['hp'],
            defence=pokemon['defence'],
            speed=pokemon['speed'],
            height=pokemon['height'],
            weight=pokemon['weight'],
            img=pokemon['img'],
        )
        new_pokemon.save()
        print(new_pokemon.name, i)
        i+=1
        if i == 1018:
            i = 10001
except Exception as e:
    print('READY')
    print(e)
