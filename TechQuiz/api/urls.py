from django.urls import path
from . import views

urlpatterns = [
    path('quiz/submit_round/', views.submit_round, name='submit_round'),
    path('game/status/', views.get_game_status, name='get_game_status'),
]
