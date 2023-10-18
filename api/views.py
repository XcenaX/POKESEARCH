from django.http import Http404
from django.shortcuts import render
from api.serializers import PokemonSerializer, FightRoomSerializer
from polls.game import get_all_pokemons, fetch_certain_pokemon
from api.models import PokedexPokemon
from polls.models import Pokemon, FightRoom
# Create your views here.
from rest_framework.response import Response
from rest_framework import viewsets

from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import FightPokemonFilter, PokedexPokemonFilter, RoomFilter
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from drf_yasg import openapi

from django.core.mail import send_mail

import datetime
import random

from polls.game import game

class PokedexPokemonViewSet(viewsets.ModelViewSet):
    #filter_backends = (SearchFilter, DjangoFilterBackend)
    #filter_backends = [DjangoFilterBackend]
    #filterset_fields = ["hp", "defence", 'attack', 'speed', 'name']
    filterset_class = PokedexPokemonFilter
    http_method_names = ['get']
    queryset = PokedexPokemon.objects.all()
    serializer_class = PokemonSerializer

    def retrieve(self, request, pk=None):
        queryset = PokedexPokemon.objects.all()
        try:            
            pokemon = PokedexPokemon.objects.get(id=pk)           
            serializer = PokemonSerializer(pokemon)
            return Response(serializer.data)
        except:
            raise Http404
        

class FightPokemonViewSet(viewsets.ModelViewSet):
    #filter_backends = (SearchFilter, DjangoFilterBackend)
    filterset_class = FightPokemonFilter
    #filterset_fields = ["hp", "defence", 'attack', 'speed', 'name']
    http_method_names = ['get', 'put', 'patch']
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer

    def retrieve(self, request, pk=None):
        queryset = Pokemon.objects.all()
        try:            
            pokemon = Pokemon.objects.get(id=pk)           
            serializer = PokemonSerializer(pokemon)
            return Response(serializer.data)
        except:
            raise Http404
        

class FightRoomViewSet(viewsets.ModelViewSet):
    #filter_backends = (SearchFilter, DjangoFilterBackend)
    #filter_backends = [DjangoFilterBackend]
    #filterset_fields = ['game_ended', 'you_win', 'rounds']
    filterset_class = RoomFilter
    http_method_names = ['get', 'post']
    queryset = FightRoom.objects.all()
    serializer_class = FightRoomSerializer

    def retrieve(self, request, pk=None):
        queryset = FightRoom.objects.all()
        try:            
            room = FightRoom.objects.get(id=pk)           
            serializer = FightRoomSerializer(room)
            return Response(serializer.data)
        except:
            raise Http404
        

class CreateFight(APIView):
    @swagger_auto_schema(
        operation_description='Создать бой между покемонами. Передается id вашего покемона',    
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['pokemon_id'],
            properties={
                'pokemon_id':openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),      
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "room":{
                            'uuid': 'some uuid',
                            'your_pokemon': {
                                "name": 'pikachu',
                                'hp': 20,
                                'defence': 20,
                                'attack': 20,
                                'speed': 20,
                                'img': 'some url'
                            },    
                            'enemy_pokemon': {
                                "name": 'raichu',
                                'hp': 25,
                                'defence': 25,
                                'attack': 25,
                                'speed': 25,
                                'img': 'some url'
                            },                         
                        },                                               
                    },                    
                }
            ),
            "401": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Error Message'                      
                    },                    
                }
            ),            
        })
    def post(self, request):    
        your_pokemon_id = request.POST.get('pokemon_id')   
        enemy_pokemon_id = random.randint(1, PokedexPokemon.objects.count)
        enemy_pokemon = PokedexPokemon.objects.get(enemy_pokemon_id) 
        pokemon = None
        try:
            pokemon = PokedexPokemon.objects.get(id=your_pokemon_id)  
        except:
            return Response({"error": "Покемон с переданным id не найден"}, status=401)        
        
        response = {
            'room':{
                'uuid': '',
                'your_pokemon': {},
                'enemy_pokemon': {},
            }
        }

        your_fight_pokemon = Pokemon.objects.create(name=pokemon.name, 
                               hp=pokemon.hp,
                               attack=pokemon.attack,
                               defence=pokemon.defence,
                               speed=pokemon.speed,
                               img=pokemon.img)

        enemy_fight_pokemon = Pokemon.objects.create(name=enemy_pokemon.name, 
                               hp=enemy_pokemon.hp,
                               attack=enemy_pokemon.attack,
                               defence=enemy_pokemon.defence,
                               speed=enemy_pokemon.speed,
                               img=enemy_pokemon.img)
        your_fight_pokemon.save()
        enemy_fight_pokemon.save()

        room = FightRoom.objects.create(your_pokemon=your_fight_pokemon, enemy_pokemon=enemy_fight_pokemon)
        room.save()

        your_serializer = PokemonSerializer(your_fight_pokemon)
        enemy_serializer = PokemonSerializer(enemy_fight_pokemon)

        response['room']['uuid'] = room.uuid
        response['room']['your_pokemon'] = your_serializer.data
        response['room']['enemy_pokemon'] = enemy_serializer.data
        
        return Response(response, status=200)  
    

class Fight(APIView):
    @swagger_auto_schema(
        operation_description='Кинуть кубик. Возвращается обновленная комната', 
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['user_input','room_uuid'],
            properties={
                'user_input':openapi.Schema(type=openapi.TYPE_STRING),
                'room_uuid':openapi.Schema(type=openapi.TYPE_STRING),                
            },
        ),       
        responses={
            "200": openapi.Response(        
                description='',        
                examples={
                    "application/json": {
                        "room":{
                            'uuid': 'some uuid',
                            'your_pokemon': {
                                "name": 'pikachu',
                                'hp': 20,
                                'defence': 20,
                                'attack': 20,
                                'speed': 20,
                                'img': 'some url'
                            },    
                            'enemy_pokemon': {
                                "name": 'raichu',
                                'hp': 25,
                                'defence': 25,
                                'attack': 25,
                                'speed': 25,
                                'img': 'some url'
                            },                         
                        },   
                        'success_attack': True,                                            
                    },                    
                }
            ),
            "401": openapi.Response(
                description='',                
                examples={
                    "application/json": {
                        "success": False,  
                        'message': 'Error Message'                      
                    },                    
                }
            ),            
        })
    def post(self, request):    
        user_input = int(request.POST["user_input"])
        room_uuid = request.POST.get('room_uuid')   
        room = None
        try:
            room = FightRoom.objects.get(uuid=room_uuid)  
        except:
            return Response({"error": "Комната с переданным uuid не найденa"}, status=401)        
        
        response = {
            'room':{
                'uuid': room.uuid,
                'your_pokemon': {},
                'enemy_pokemon': {},
                'success_attack': True
            }
        }

        pc_choice = random.randint(1, 10)
        
        success_attack = False
        if not room.game_ended:          
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
            elif room.enemy_pokemon.hp <= 0:
                game_ended = True
                room.ended_at = datetime.now()
                room.game_ended = game_ended
                room.you_win = True                
        else:
            return Response({"success": False, "error": "Битва уже окончена, нельзя кидать кубик"})
        room.save()

        your_serializer = PokemonSerializer(room.your_pokemon)
        enemy_serializer = PokemonSerializer(room.enemy_pokemon)

        response['room']['your_pokemon'] = your_serializer.data
        response['room']['enemy_pokemon'] = enemy_serializer.data
        response['room']['success_attack'] = success_attack
        
        return Response(response, status=200)  
    

class FastFight(APIView):
    def get(self, request, uuid):              
        room = None
        try:
            room = FightRoom.objects.get(uuid=uuid)  
        except:
            return Response({"error": "Комната с переданным uuid не найденa"}, status=401)        
        
        response = {
            'room':{
                'uuid': room.uuid,
                'your_pokemon': {},
                'enemy_pokemon': {},
                'you_win': False
            },
            'winner': ''
        }

        logs, winner = game(room)

        your_serializer = PokemonSerializer(room.your_pokemon)
        enemy_serializer = PokemonSerializer(room.enemy_pokemon)

        response['room']['your_pokemon'] = your_serializer.data
        response['room']['enemy_pokemon'] = enemy_serializer.data
        response['room']['winner'] = winner
        response['room']['logs'] = logs
        
        return Response(response, status=200) 