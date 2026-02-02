from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from instructor.models import GameState
from .utils import get_questions_from_sheet
import json

def round_1_view(request):
    # Fetch questions from Google Sheet
    questions = get_questions_from_sheet()
    
    # Optional: Check if Round 1 is active
    try:
        game_state = GameState.load()
        # if game_state.round_status != 'ONGOING' or game_state.active_round != 1:
        #     return redirect('waiting_room')
    except:
        pass

    # Sanitize questions (remove correct answer)
    frontend_questions = []
    for q in questions:
        frontend_questions.append({
            'id': q['id'],
            'q': q['q'],
            'options': q['options']
            # 'correct' is explicitly excluded
        })

    context = {
        'questions_json': frontend_questions
    }
    return render(request, 'round_1/round_1.html', context)
