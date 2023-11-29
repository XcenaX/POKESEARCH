from random import randint
from django.http import HttpResponse
from django.test import TestCase
from polls.models import Pokemon, FightRoom
from api.models import PokedexPokemon
import uuid
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from bs4 import BeautifulSoup
import json

host = "127.0.0.1:8000"

class PokemonModelTest(TestCase):

    def setUp(self):
        # Создаем экземпляр Pokemon для тестирования
        Pokemon.objects.create(
            name="pikachu",
            pokemon_id=25,
            img="link_to_img",
            weight=6,
            height=4,
            attack=55,
            hp=35,
            defence=40,
            speed=90
        )

    def test_pokemon_creation(self):
        # Проверяем, что покемон был корректно создан
        pikachu = Pokemon.objects.get(name="pikachu")
        self.assertEqual(pikachu.pokemon_id, 25)
        self.assertEqual(pikachu.img, "link_to_img")
        self.assertEqual(pikachu.weight, '6')
        self.assertEqual(pikachu.height, '4')
        self.assertEqual(pikachu.attack, 55)
        self.assertEqual(pikachu.hp, 35)
        self.assertEqual(pikachu.defence, 40)
        self.assertEqual(pikachu.speed, 90)

    def test_default_values(self):
        # Создаем покемона без явного задания значений
        default_pokemon = Pokemon.objects.create(name="default")
        self.assertEqual(default_pokemon.pokemon_id, 1)
        self.assertEqual(default_pokemon.img, "")
        self.assertEqual(default_pokemon.weight, 0)
        self.assertEqual(default_pokemon.height, 0)
        self.assertEqual(default_pokemon.attack, 0)
        self.assertEqual(default_pokemon.hp, 0)
        self.assertEqual(default_pokemon.defence, 0)
        self.assertEqual(default_pokemon.speed, 0)

    def test_str_representation(self):
        pikachu = Pokemon.objects.get(name="pikachu")
        self.assertEqual(str(pikachu), "pikachu")



class FightRoomModelTest(TestCase):
    def setUp(self):
        # Создаем двух покемонов для тестирования
        self.pokemon1 = Pokemon.objects.create(name="bulbasaur")
        self.pokemon2 = Pokemon.objects.create(name="charmander")

        # Создаем экземпляр FightRoom для тестирования
        self.fight_room = FightRoom.objects.create(
            your_pokemon=self.pokemon1,
            enemy_pokemon=self.pokemon2,
            game_ended=False,
            you_win=False,
            rounds=3
        )

    def test_fight_room_creation(self):
        # Проверяем, что комната для боя была корректно создана
        self.assertEqual(self.fight_room.your_pokemon.name, "bulbasaur")
        self.assertEqual(self.fight_room.enemy_pokemon.name, "charmander")
        self.assertFalse(self.fight_room.game_ended)
        self.assertFalse(self.fight_room.you_win)
        self.assertEqual(self.fight_room.rounds, 3)

    def test_fight_room_uuid(self):
        # Проверяем, что UUID был правильно создан
        self.assertIsInstance(self.fight_room.uuid, uuid.UUID)

    def test_str_representation(self):
        # Проверяем строковое представление объекта FightRoom
        self.assertEqual(str(self.fight_room), "bulbasaur VS charmander")


class PokedexPokemonModelTest(TestCase):

    def setUp(self):
        # Создаем экземпляр PokedexPokemon для тестирования
        PokedexPokemon.objects.create(
            name="eevee",
            attack=55,
            hp=65,
            defence=50,
            img="link_to_img",
            weight=6.5,
            height=3,
            speed=55
        )

    def test_pokedex_pokemon_creation(self):
        # Проверяем, что покемон из покедекса был корректно создан
        eevee = PokedexPokemon.objects.get(name="eevee")
        self.assertEqual(eevee.attack, 55)
        self.assertEqual(eevee.hp, 65)
        self.assertEqual(eevee.defence, 50)
        self.assertEqual(eevee.img, "link_to_img")
        self.assertEqual(eevee.weight, '6.5')
        self.assertEqual(eevee.height, '3')
        self.assertEqual(eevee.speed, '55')

    def test_str_representation(self):
        eevee = PokedexPokemon.objects.get(name="eevee")
        self.assertEqual(str(eevee), "eevee")
 

class PokemonFightTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.pokedex_p1 = PokedexPokemon.objects.create(attack=150, hp=50, defence=10, name='bulbasaur')
        self.pokedex_p2 = PokedexPokemon.objects.create(attack=190, hp=39, defence=15, name='charmander')

    def test_fight(self):
        url = reverse('polls:api_create_fight')
        response = self.client.post(url, {'pokemon_id': self.pokedex_p1.id})
        
        data = json.loads(response.content)        
        room_uuid = data['room']['uuid'] 
        
        self.assertTrue(FightRoom.objects.exists())    
   
        url = reverse('polls:make_move')
        game_ended = False
        
        limit = 100
        while not game_ended:
            user_number = randint(1,10)
            response = self.client.post(url, {'user_input': user_number, 'room_uuid': room_uuid})
            response_data = json.loads(response.content)
            game_ended = response_data.get("game_ended", False)
            limit -= 1
            if limit == 0:
                self.assertTrue(game_ended, True)

        
        self.assertTrue(game_ended)
    
    def send_ftp(self):
        url = reverse('polls:send_to_ftp')
        response = self.client.post(url, {'pokemon_id': self.pokedex_p1.id})
        
        data = json.loads(response.content)        
        self.assertEqual(data['success'], True) 
    
    def send_email(self):
        url = reverse('polls:send_fight')
        response = self.client.post(url, {'pokemon_id': self.pokedex_p1.id})
        
        data = json.loads(response.content)        
        self.assertEqual(data['success'], True)
        

class PokemonFilterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.pokedex_p1 = PokedexPokemon.objects.create(attack=20, hp=50, name='bulbasaur')
        self.pokedex_p2 = PokedexPokemon.objects.create(attack=30, hp=39, name='charmander')

    def test_filter_pokemon_by_attack(self):
        url = reverse('polls:home') + '?title=cha'
        response = self.client.get(url)
        
        # Парсим html и смотрим сколько покемонов вернулось
        soup = BeautifulSoup(response.content, 'html.parser')
        ul = soup.find('ul', class_='list-unstyled')
        count = len(ul.find_all('a')) if ul else 0

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(count, 1)


class GetFightsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Создаем двух покемонов для тестирования
        self.pokemon1 = Pokemon.objects.create(name="bulbasaur")
        self.pokemon2 = Pokemon.objects.create(name="charmander")

        # Создаем экземпляр FightRoom для тестирования
        self.fight_room = FightRoom.objects.create(
            your_pokemon=self.pokemon1,
            enemy_pokemon=self.pokemon2,
            game_ended=False,
            you_win=False,
            rounds=3
        )

    # TODO
    def test_get_all_fights(self):
        url = reverse('polls:all_fights')
        response = self.client.get(url)
        
        soup = BeautifulSoup(response.content, 'html.parser')
        ul = soup.find('ul', class_='list-unstyled')
        count = len(ul.find_all('a')) if ul else 0

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(count, 1)




class APITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_filter_pokemon(self):
        url = host + '/pokemons/?title=que'
        response = self.client.get(url)
        
        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), 3)
    
    def test_get_pokemon(self):
        url = host + '/pokemons/1/'
        response = self.client.get(url)
        
        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['hp'], 45)
        self.assertEqual(data['defence'], 49)
        self.assertEqual(data['attack'], 49)
        self.assertEqual(data['name'], 'bulbasaur')
        self.assertEqual(data['speed'], 45)
    
    def test_send_ftp(self):
        url = host + '/send-to-ftp/1/'
        response = self.client.post(url)
        
        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['success'], True)

    def test_fight(self):
        url = host + '/create-fight/'
        response = self.client.post(url)
        
        data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['success'], True)