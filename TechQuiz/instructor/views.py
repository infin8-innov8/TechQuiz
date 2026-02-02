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
    
    # Imports for Round 3 Logic
    from .models import Round3Question, Round3Score, Round1Score, Round2Score, BerserkLog
    
    # Identify Qualified Teams (Top 10 from Round 2)
    r2_scores = Round2Score.objects.select_related('team').order_by('-score', 'completion_time')
    qualified_teams_r2 = [s.team for s in r2_scores[:10]] # Top 10
    
    # Ensure R3Score objects exist for all qualified teams
    for team in qualified_teams_r2:
        Round3Score.objects.get_or_create(team=team)
    
    questions = Round3Question.objects.all().order_by('sequence_order')
    scores = Round3Score.objects.filter(team__in=qualified_teams_r2).order_by('-score')
    active_question = Round3Question.objects.filter(is_active=True).first()

    if request.method == 'POST':
        if 'active_round' in request.POST: # Game State Update
            form = GameStateForm(request.POST, instance=game_state)
            if form.is_valid():
                form.save()
                messages.success(request, f"Game State Updated: Round {game_state.active_round} is now {game_state.round_status}")
                return redirect('instructor_dashboard')
        
        else: # Round 3 Actions
            action = request.POST.get('action')
            
            if action == 'activate_question':
                q_id = request.POST.get('question_id')
                Round3Question.objects.update(is_active=False) 
                q = Round3Question.objects.get(id=q_id)
                q.is_active = True
                q.save()
                messages.success(request, f"Activated Question: {q.question_text}")
                
            elif action == 'deactivate_all':
                Round3Question.objects.update(is_active=False)
                messages.info(request, "All questions deactivated.")
                
            elif action == 'update_score':
                team_id = request.POST.get('team_id')
                try:
                    points = int(request.POST.get('points'))
                except (ValueError, TypeError):
                    points = 0
                    
                team = Team.objects.get(id=team_id)
                score_obj, created = Round3Score.objects.get_or_create(team=team)
                score_obj.score += points
                score_obj.save()
                messages.success(request, f"Updated score for {team.team_name} by {points}.")
            
            return redirect('instructor_dashboard')
            
    else:
        form = GameStateForm(instance=game_state)

    context = {
        'form': form,
        'game_state': game_state,
        'questions': questions,
        'scores': scores,
        'active_question': active_question,
        'teams': qualified_teams_r2
    }
            
    return render(request, 'instructor/dashboard.html', context)
