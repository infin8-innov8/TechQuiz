from django.contrib import admin
from .models import GameState, Round1Score, Round2Score, Round3Score

@admin.register(GameState)
class GameStateAdmin(admin.ModelAdmin):
    list_display = ('active_round', 'round_status', 'updated_at')
    # Prevent creating multiple GameState instances if one exists is handled in model save, 
    # but removing 'add' permission might be nicer. For now, standard admin is fine.

@admin.register(Round1Score)
class Round1ScoreAdmin(admin.ModelAdmin):
    list_display = ('team', 'score', 'completion_time')
    search_fields = ('team__team_name', 'team__member1_name')
    list_filter = ('score', 'completion_time')

@admin.register(Round2Score)
class Round2ScoreAdmin(admin.ModelAdmin):
    list_display = ('team', 'score', 'completion_time')
    search_fields = ('team__team_name',)

@admin.register(Round3Score)
class Round3ScoreAdmin(admin.ModelAdmin):
    list_display = ('team', 'score', 'completion_time')
    search_fields = ('team__team_name',)
