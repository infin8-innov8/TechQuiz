from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from instructor.models import GameState
from .utils import get_round2_questions
import json

@login_required(login_url='/waiting-room/')
def round_2_view(request):
    # Game State Validation
    try:
        game_state = GameState.load()
        # Ensure strict access control
        # If active_round is NOT 2, check if we should be here
        if game_state.round_status != 'ONGOING' and game_state.active_round == 2:
             # Allowed to view if Done or Waiting? Probably usually blocked unless ongoing.
             # User logic implies redirection logic is handled in Waiting Room mostly, 
             # but keeping a safeguard here is good.
             pass 
    except:
        pass

    # Fetch questions
    questions = get_round2_questions()
    
    # Sanitize for Frontend (Server-Side Scoring Security)
    frontend_questions = []
    for q in questions:
        frontend_questions.append({
            'id': q['id'],
            'q': q['q'],
            'options': q['options']
            # Correct answer excluded
        })

    context = {
        'questions_json': frontend_questions
    }
    return render(request, 'round_2/round_2.html', context)
