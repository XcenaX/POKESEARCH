from rest_framework import serializers


class PokemonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    hp = serializers.IntegerField()
    defence = serializers.IntegerField()
    attack = serializers.IntegerField()
    name = serializers.CharField(max_length=40)
    speed = serializers.IntegerField()
    img = serializers.CharField()


class FightRoomSerializer(serializers.Serializer):
    uuid = serializers.CharField()
    your_pokemon = PokemonSerializer()
    enemy_pokemon = PokemonSerializer()
    game_ended = serializers.BooleanField()
    you_win = serializers.BooleanField()
    rounds = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()
