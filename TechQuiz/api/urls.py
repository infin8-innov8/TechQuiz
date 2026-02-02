from django.urls import path
from . import views

urlpatterns = [
    path('quiz/submit_round/', views.submit_round, name='submit_round'),
    path('game/status/', views.get_game_status, name='get_game_status'),
    path('leaderboard/', views.get_leaderboard, name='get_leaderboard'),
    path('quiz/berserk/', views.berserk_click, name='berserk_click'),
]
