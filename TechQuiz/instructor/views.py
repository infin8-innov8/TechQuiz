from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .forms import GameStateForm
from .models import GameState, Round3Score, Round3Question
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
    

    scores = Round3Score.objects.filter(team__in=qualified_teams_r2).order_by('-score')


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
                # LOCK ALL: Lock, but don't reset "current"
                current = game_state.current_round3_question
                if current:
                    current.is_active = False
                    current.save()
                    messages.info(request, "Question Locked.")
                else:
                    Round3Question.objects.update(is_active=False)
                    messages.info(request, "System Locked.")

            elif action == 'toggle_activation': # New Action: Unlock/Lock
                current = game_state.current_round3_question
                if current:
                    if current.is_active:
                        # Lock it
                        current.is_active = False
                        current.save()
                        messages.info(request, f"Locked Q{current.sequence_order}")
                    else:
                        # Unlock it (Start Berserk)
                        current.is_active = True
                        current.activated_at = timezone.now()
                        current.save()
                        messages.success(request, f"UNLOCKED BERSERK for Q{current.sequence_order}!")
                else:
                    messages.warning(request, "No question selected to unlock.")

            elif action == 'next_question':
                current = game_state.current_round3_question
                
                # Try to find existing next question
                if current:
                    next_q = Round3Question.objects.filter(sequence_order__gt=current.sequence_order).order_by('sequence_order').first()
                else:
                    next_q = Round3Question.objects.order_by('sequence_order').first()

                # If no existing next question, create one (Arbitrary Number support)
                if not next_q:
                    new_order = (current.sequence_order + 1) if current else 1
                    next_q = Round3Question.objects.create(
                        sequence_order=new_order,
                        question_text=f"Physical Question {new_order}"
                    )

                if next_q:
                    # Lock the previous one and the new one for safety
                    if current:
                        current.is_active = False
                        current.save()
                    
                    game_state.current_round3_question = next_q
                    game_state.save()
                    next_q.is_active = False # Default to locked
                    next_q.save()
                    messages.success(request, f"Selected Next Question: Q{next_q.sequence_order}")

            elif action == 'prev_question':
                current = game_state.current_round3_question
                if current:
                    # Lock current
                    current.is_active = False
                    current.save()

                    prev_q = Round3Question.objects.filter(sequence_order__lt=current.sequence_order).order_by('-sequence_order').first()
                    
                    if prev_q:
                        game_state.current_round3_question = prev_q
                        game_state.save()
                        messages.success(request, f"Selected Previous Question: Q{prev_q.sequence_order}")
                    else:
                        messages.warning(request, "Start of questions reached.")
                else:
                    messages.info(request, "No question selected.")
            
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

        'scores': scores,
        'active_question': game_state.current_round3_question, # Current Selected
        'teams': qualified_teams_r2
    }
            
    return render(request, 'instructor/dashboard.html', context)