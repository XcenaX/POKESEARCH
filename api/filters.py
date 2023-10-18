import django_filters
from .models import PokedexPokemon
from polls.models import Pokemon, FightRoom

class PokedexPokemonFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains') 
    hp = django_filters.CharFilter(lookup_expr='icontains') 
    defence = django_filters.CharFilter(lookup_expr='icontains') 
    attack = django_filters.CharFilter(lookup_expr='icontains') 
    speed = django_filters.CharFilter(lookup_expr='icontains') 

    class Meta:
        model = PokedexPokemon
        fields = ['name', "hp", "defence", 'attack', 'speed'] 


class FightPokemonFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains') 
    hp = django_filters.CharFilter(lookup_expr='icontains') 
    defence = django_filters.CharFilter(lookup_expr='icontains') 
    attack = django_filters.CharFilter(lookup_expr='icontains') 
    speed = django_filters.CharFilter(lookup_expr='icontains') 

    class Meta:
        model = Pokemon
        fields = ['name', "hp", "defence", 'attack', 'speed'] 


class RoomFilter(django_filters.FilterSet):
    game_ended = django_filters.CharFilter(lookup_expr='icontains') 
    you_win = django_filters.CharFilter(lookup_expr='icontains') 
    rounds = django_filters.CharFilter(lookup_expr='icontains') 
    created_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    ended_at = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = FightRoom
        fields = ['game_ended', "you_win", "rounds", 'created_at', 'ended_at'] 