from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger        
from datetime import datetime, timezone
COUNT_BLOCKS_ON_PAGE = 20
POKEMONS_COUNT = 1292
LAST_PAGE = POKEMONS_COUNT // COUNT_BLOCKS_ON_PAGE
import re
from .game import game, get_pokemons_by_page, fetch_certain_pokemon, get_pages

from .models import Pokemon, FightRoom
from api.models import PokedexPokemon
from django.core.mail import send_mail
from area.settings import EMAIL_HOST_USER
import random

from users.modules.functions import get_current_user

from api.serializers import PokemonSerializer

from django.core.cache import cache

def pokemon(request, id): 
    current_user = get_current_user(request)
    if not cache.get('pokemon{0}'.format(id), None):
        try:        
            pokemon = PokedexPokemon.objects.get(id=id)
            cache.set('pokemon{0}'.format(id), pokemon, 3600)
        except:
            return redirect(reverse('polls:home'))        
    else:
        pokemon = cache.get('pokemon{0}'.format(id), None)

    picked_id = 0
    try:
        picked_id = request.session["pokemon"]
    except:
        pass
    is_picked = picked_id == id

    return render(request, 'page.html', {
        'current_user': current_user,
        "pokemon": pokemon,
        'is_picked': is_picked,
        'picked_id': picked_id
    })  

def pick_pokemon(request, id):     
    request.session["pokemon"] = id
    return redirect(request.META.get('HTTP_REFERER'))
    
def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def main(request):             
    current_user = get_current_user(request)
    title = request.GET.get('title', "")
    page = request.GET.get('page')  
    pokemons = []   
    try:
        page = int(page)
    except:
        page = 1   

    if not cache.get("page{0}title{1}".format(page, title), None):
        pokemons = PokedexPokemon.objects.all()
        
        if title:    
            pokemons = pokemons.filter(name__icontains=title)

        paginator = Paginator(pokemons, COUNT_BLOCKS_ON_PAGE)     
            
        pages = get_pages(paginator.page_range, page)
        pokemons = get_pokemons_by_page(pokemons, page)
        
        # cached_pokemons = []
        # for pokemon in pokemons:
        #     serializer = PokemonSerializer(pokemon)
        #     cached_pokemons.append(serializer.data)
        cache.set("page{0}title{1}".format(page, title), pokemons, 3600)
    else:
        pokemons = cache.get("page{0}title{1}".format(page, title))       
        paginator = Paginator(pokemons, COUNT_BLOCKS_ON_PAGE)
        pages = get_pages(range(len(pokemons)//COUNT_BLOCKS_ON_PAGE), page)



    return render(request, 'news.html', {
        "current_user": current_user,
        'snews': pokemons,
        "title": title,     
        "pages": pages,
    })  


def quick_fight(request, room_id): 
    room = None
    try:
        room = FightRoom.objects.get(uuid=room_id) 
        print(room)
        logs, winner = game(room)
    except Exception as e:
        print(e)
        return redirect(reverse("polls:home"))
    
    return redirect(reverse('polls:fight', args=(room_id,)))


def create_fight(request): 
    if request.method == "GET":        
        return redirect(request.META.get('HTTP_REFERER'))
    elif request.method == "POST":
        current_user = get_current_user(request)
        your_pokemon_id = int(request.POST["your_pokemon_id"])
        enemy_pokemon_id = int(request.POST["enemy_pokemon_id"])
        
        your_pokemon = fetch_certain_pokemon(your_pokemon_id)
        enemy_pokemon = fetch_certain_pokemon(enemy_pokemon_id)

        db_your_pokemon = Pokemon.objects.create(name=your_pokemon['name'],
                                                height=your_pokemon['height'],
                                                weight=your_pokemon['weight'],
                                                hp=your_pokemon["hp"], 
                                                attack=your_pokemon["attack"], 
                                                defence=your_pokemon["defence"],
                                                speed=your_pokemon["speed"],
                                                img=your_pokemon["img"])
        
        db_enemy_pokemon = Pokemon.objects.create(name=enemy_pokemon['name'],
                                                height=enemy_pokemon['height'],
                                                weight=enemy_pokemon['weight'],
                                                hp=enemy_pokemon["hp"], 
                                                attack=enemy_pokemon["attack"], 
                                                defence=enemy_pokemon["defence"],
                                                speed=enemy_pokemon["speed"],
                                                img=enemy_pokemon["img"])
        db_your_pokemon.save()
        db_enemy_pokemon.save()

        room = FightRoom.objects.create(your_pokemon=db_your_pokemon, enemy_pokemon=db_enemy_pokemon, user=current_user)
        room.save()

        return HttpResponseRedirect(reverse('polls:fight', args=(room.uuid,)))


def fight(request, room_id): 
    current_user = get_current_user(request)
    room = None
    try:
        room = FightRoom.objects.get(uuid=room_id)
    except:
        return redirect(request.META.get('HTTP_REFERER'))
    game_ended = room.game_ended

    if request.method == "GET":        
        return render(request, 'fight.html', {
            "room": room,
            "game_ended": game_ended,
        })
    elif request.method == "POST":
        success_attack = False
        if not game_ended:
            user_input = int(request.POST["user_input"])
            pc_choice = random.randint(1,10)            
            if user_input%2==0 and pc_choice%2==0 or user_input%2==1 and pc_choice%2==1:
                attack = round(room.your_pokemon.attack * (room.enemy_pokemon.defence/230))
                room.enemy_pokemon.hp -= attack
                room.enemy_pokemon.save()
                success_attack = True
            else:
                attack = round(room.enemy_pokemon.attack * (room.your_pokemon.defence/230))
                room.your_pokemon.hp -= attack
                room.your_pokemon.save()
            
            
            if room.your_pokemon.hp <= 0:
                game_ended = True
                room.game_ended = game_ended
                room.ended_at = datetime.now()
                room.save()                            
            elif room.enemy_pokemon.hp <= 0:
                game_ended = True
                room.ended_at = datetime.now()
                room.game_ended = game_ended
                room.you_win = True
                room.save()
            
        return render(request, 'fight.html', {
            "current_user": current_user,
            "room": room,
            "game_ended": game_ended,
            "success_attack": success_attack,
        })
    

def send_fight(request):
    if request.method == "POST":
        room_id = request.POST.get('room', None)
        room = None
        email = request.POST.get("email", None)
        
        if room_id:
            room = FightRoom.objects.get(id=room_id)
        
        # if not logs:            
        #     winner = room.your_pokemon.name if room.you_win else room.enemy_pokemon.name            
        #     message = "В жетсочайшем бою {0}VS{1}\nПобедитель:{2}".format(room.your_pokemon.name, room.enemy_pokemon.name, winner)

        send_mail(
            "Результат боя",
            room.logs,
            EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))



def all_fights(request): 
    current_user = get_current_user(request)
    rooms = FightRoom.objects.all()

    page = request.GET.get('page')        
    try:
        page = int(page)
    except:
        page = 1

    if len(rooms) > 20:    
        rooms = rooms[page*20 : page*20+20]

    pages = []
    if len(rooms) > 20:
        for i in range(page-2, page+3):
            pages.append(i)

    return render(request, 'all_fights.html', {
        "current_user": current_user,
        "rooms": rooms,   
        "pages": pages,     
    })