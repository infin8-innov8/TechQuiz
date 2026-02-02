from django import forms
from .models import GameState

class GameStateForm(forms.ModelForm):
    class Meta:
        model = GameState
        fields = ['active_round', 'round_status']
        widgets = {
            'active_round': forms.Select(attrs={'class': 'form-select'}),
            'round_status': forms.Select(attrs={'class': 'form-select'}),
        }
