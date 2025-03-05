from django.urls import path
from .views import create_pit, create_table, add_player, add_hourly_rundown, get_rundowns, update_player_funds

urlpatterns = [
    path('pits/create/', create_pit),  # Supervisor-only
    path('tables/create/', create_table),  # Supervisor-only
    path('players/add/', add_player),  # PIT Boss-only
    path('players/update/<int:player_id>/', update_player_funds),  # PIT Boss-only
    path('rundowns/add/', add_hourly_rundown),  # PIT Boss-only
    path('rundowns/view/', get_rundowns),  # Supervisor-only
]

