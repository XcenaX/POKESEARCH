from django.urls import path, re_path, include
from . import views

from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.views import FightPokemonViewSet, PokedexPokemonViewSet, FightRoomViewSet, CreateFight, Fight

schema_view = get_schema_view(
   openapi.Info(
      title="Pokemon API",
      default_version='v1',
      description="Pokemon API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)
router = routers.SimpleRouter()

router.register(r'pokemons', PokedexPokemonViewSet)
router.register(r'fight_pokemons', FightPokemonViewSet)
router.register(r'rooms', FightRoomViewSet)

app_name = 'polls'
urlpatterns = [
    path('', views.main, name='home'),
    path('docs/',  schema_view.with_ui( cache_timeout=0)),#'redoc',
    re_path('api/', include(router.urls)),
    path('api/create_fight/', CreateFight.as_view(), name='api_create_fight'),    
    path('api/fight/', Fight.as_view(), name='make_move'),    

    
    path('pokemon/<int:id>/', views.pokemon, name='pokemon'),
    path('pick_pokemon/<int:id>/', views.pick_pokemon, name='pick_pokemon'),    
    path('quick_fight/<slug:room_id>/', views.quick_fight, name='quick_fight'),    
    path('fight/<slug:room_id>/', views.fight, name='fight'),    
    path('create_fight/', views.create_fight, name='create_fight'),    
    path('all_fights/', views.all_fights, name='all_fights'),    
    path('send_fight/', views.send_fight, name='send_fight'),    

]