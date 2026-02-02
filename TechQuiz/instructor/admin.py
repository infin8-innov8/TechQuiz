from django.contrib import admin
from .models import GameState, Round1Score, Round2Score, Round3Score, Round3Question, BerserkLog

@admin.register(GameState)
class GameStateAdmin(admin.ModelAdmin):
    list_display = ('id', 'active_round', 'round_status', 'updated_at')
    list_display_links = ('id',)
    list_editable = ('active_round', 'round_status')

@admin.register(Round1Score)
class Round1ScoreAdmin(admin.ModelAdmin):
    list_display = ('team', 'score', 'completion_time')

@admin.register(Round2Score)
class Round2ScoreAdmin(admin.ModelAdmin):
    list_display = ('team', 'score', 'completion_time')

@admin.register(Round3Score)
class Round3ScoreAdmin(admin.ModelAdmin):
    list_display = ('team', 'score', 'completion_time')

@admin.register(Round3Question)
class Round3QuestionAdmin(admin.ModelAdmin):
    list_display = ('sequence_order', 'question_text', 'is_active')
    list_editable = ('is_active',)

@admin.register(BerserkLog)
class BerserkLogAdmin(admin.ModelAdmin):
    list_display = ('team', 'question', 'timestamp', 'is_illegal')
    list_filter = ('question', 'is_illegal')
    readonly_fields = ('timestamp',)
    search_fields = ('team__team_name',)
