import os
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TechQuiz.settings')
django.setup()

from instructor.models import GameState

try:
    game_state = GameState.load()
    print(f"Current Game State:")
    print(f"  Active Round: {game_state.active_round}")
    print(f"  Round Status: {game_state.round_status}")
    
    if game_state.active_round != 2:
        print("WARNING: Active round is NOT 2. Round 2 view might block access.")
    if game_state.round_status != 'ONGOING':
        print("WARNING: Round status is NOT ONGOING. Round 2 view might block access.")
        
except Exception as e:
    print(f"Error accessing GameState: {e}")
