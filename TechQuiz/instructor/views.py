from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import GameStateForm
from .models import GameState
from registration_n_login.models import Team

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def instructor_dashboard(request):
    game_state = GameState.load()
    
    if request.method == 'POST':
        form = GameStateForm(request.POST, instance=game_state)
        if form.is_valid():
            form.save()
            messages.success(request, f"Game State Updated: Round {game_state.active_round} is now {game_state.round_status}")
            return redirect('instructor_dashboard')
    else:
        form = GameStateForm(instance=game_state)

    context = {
        'form': form,
        'game_state': game_state
    }
            
    return render(request, 'instructor/dashboard.html', context)
