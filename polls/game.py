import datetime
import requests
import random
import time
from polls.models import Pokemon, FightRoom

COUNT_BLOCKS_ON_PAGE = 20

def get_pages(pages, page):
    if len(pages) == 0:
        return []
    new_pages = [1]
    for i in range(page-5, page+5):
        if i > 1 and i < pages[len(pages)-1]:
            new_pages.append(i)
    new_pages.append(pages[len(pages)-1])
    return new_pages

def fetch_certain_pokemon(poke_name):
    url = 'https://pokeapi.co/api/v2/pokemon/{}/'.format(poke_name)
    response = requests.get(url)
    pokemon = response.json()
    return dict(name=pokemon['name'], id=pokemon['id'], height=pokemon['height'], weight=pokemon['weight'],
                experience=pokemon['base_experience'], hp=pokemon["stats"][0]["base_stat"], 
                attack=pokemon["stats"][1]["base_stat"], 
                defence=pokemon["stats"][2]["base_stat"],
                speed=pokemon["stats"][5]["base_stat"],
                img=pokemon["sprites"]["front_default"])


def get_all_pokemons():
    url = 'https://pokeapi.co/api/v2/pokemon/?limit=1300'
    response = requests.get(url)
    pokemons = response.json()
    return pokemons["results"]


def get_pokemons_by_page(pokemons, page):
    if len(pokemons) < COUNT_BLOCKS_ON_PAGE:
        return pokemons
    data = pokemons[page*COUNT_BLOCKS_ON_PAGE: page*COUNT_BLOCKS_ON_PAGE+COUNT_BLOCKS_ON_PAGE]
    return data

def make_attack(attacker, target):
    attack = ( ((2*1)/5 * (1 * (attacker["attack"]/target["defence"])) ) / 50 ) + 2
    attack = round(attacker["attack"] * (target["defence"]/230))
    
    if attack < 1:
        attack = 1
    target.hp = target.hp - attack
    return attack

def game_ended(your_pokemon, enemy_pokemon):
    return your_pokemon.hp <= 0 or enemy_pokemon.hp <= 0

def game(room: FightRoom):
    logs = ""
    
    logs += 'Ваш покемон: {}\n'.format(room.your_pokemon.name)
    logs += 'Покемон соперника: {}\n\n'.format(room.enemy_pokemon.name)

    logs += 'Ваши характеристики id:{}, атака: {}, hp: {}, защита: {}, скорость: {}\n'.format(room.your_pokemon.id,                                                                                
                                                                                                room.your_pokemon.attack,
                                                                                                room.your_pokemon.hp,
                                                                                                room.your_pokemon.defence,
                                                                                                room.your_pokemon.speed,)
    
    logs += 'Характеристики врага id:{}, атака: {}, hp: {}, защита: {}, скорость: {}\n\n'.format(room.enemy_pokemon.id,   
                                                                                                room.enemy_pokemon.attack,
                                                                                                room.enemy_pokemon.hp,
                                                                                                room.enemy_pokemon.defence,
                                                                                                room.enemy_pokemon.speed,)
        
    battle_round = 1
    while True:
        user_choice = random.randint(1, 10)
        pc_choice = random.randint(1, 10)

        logs += "\nRound {}:\n".format(battle_round)
        logs += "Кубик противника: {0} | Ваш кубик: {1}\n".format(pc_choice, user_choice)

        if user_choice%2==0 and pc_choice%2==0 or user_choice%2==1 and pc_choice%2==1:
                attack = round(room.your_pokemon.attack * (room.enemy_pokemon.defence/230))
                room.enemy_pokemon.hp -= attack
                room.enemy_pokemon.save()
                logs += "{} нанес {} урона покемону {}. У него осталось {} hp\n".format(room.your_pokemon.name, attack, room.enemy_pokemon.name, room.enemy_pokemon.hp)
                
        else:
            attack = round(room.enemy_pokemon.attack * (room.your_pokemon.defence/230))
            room.your_pokemon.hp -= attack
            room.your_pokemon.save()
            logs += "{} нанес {} урона покемону {}. У него осталось {} hp\n".format(room.enemy_pokemon.name, attack, room.your_pokemon.name, room.your_pokemon.hp)

        
        
        if room.your_pokemon.hp <= 0:
            game_ended = True
            room.game_ended = game_ended
            room.ended_at = datetime.datetime.now()
            break                       
        elif room.enemy_pokemon.hp <= 0:
            game_ended = True
            room.ended_at = datetime.datetime.now()
            room.game_ended = game_ended
            room.you_win = True
            break

        battle_round+=1

    winner = "Вы"
    if room.your_pokemon.hp <= 0:
        winner = "Противник"
    logs += "Игра окончена! Победитель: {}\n".format(winner)
    room.logs = logs
    room.save()
    return logs, winner
        
  