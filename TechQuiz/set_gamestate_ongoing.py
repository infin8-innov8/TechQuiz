import os
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TechQuiz.settings')
django.setup()

from instructor.models import GameState

try:
    game_state = GameState.load()
    print(f"Old Status: {game_state.round_status}")
    game_state.round_status = 'ONGOING'
    game_state.active_round = 2
    game_state.save()
    print(f"New Status: {game_state.round_status}")
    print("Game set to Round 2 ONGOING.")
        
except Exception as e:
    print(f"Error updating GameState: {e}")
