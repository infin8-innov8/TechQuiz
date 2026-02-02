from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from registration_n_login.models import Team
from instructor.models import Round1Score

@csrf_exempt
def submit_round(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            team_id = data.get('team_id')
            answers = data.get('answers', []) # Expecting list of {question_id: x, selected_option: y}
            round_num = data.get('round')
            
            if not team_id:
                return JsonResponse({'error': 'Team ID required'}, status=400)
                
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                 return JsonResponse({'error': 'Team not found'}, status=404)
                 
            # Save Score
            if round_num == 1:
                # SERVER-SIDE SCORING
                # Fetch master questions (cached or live)
                # Ideally, we should cache this to avoid hitting Google Sheets every submit.
                # Since the scale is small, we'll fetch live for correctness first.
                from round_1.utils import get_questions_from_sheet
                master_questions = get_questions_from_sheet()
                
                # Convert master questions to a dict for easy lookup: {id: correct_index}
                correct_answers = {q['id']: q['correct'] for q in master_questions}
                
                score = 0
                for ans in answers:
                    q_id = ans.get('question_id')
                    selected = ans.get('selected_option')
                    
                    if q_id in correct_answers and correct_answers[q_id] == selected:
                        score += 10
                
                # Update or create logic
                Round1Score.objects.update_or_create(
                    team=team,
                    defaults={
                        'score': score,
                        'completion_time': timezone.localtime(timezone.now()).time() # High precision IST time
                    }
                )
                
                return JsonResponse({
                    'success': True, 
                    'qualified': True, 
                    'score': score
                })
            elif round_num == 2:
                # SERVER-SIDE SCORING ROUND 2
                from round_2.utils import get_round2_questions
                master_questions = get_round2_questions()
                
                correct_answers = {q['id']: q['correct'] for q in master_questions}
                
                score = 0
                for ans in answers:
                    q_id = ans.get('question_id')
                    try:
                        selected = int(ans.get('selected_option'))
                    except (ValueError, TypeError):
                        continue
                        
                    if q_id in correct_answers and correct_answers[q_id] == selected:
                        score += 10 # 10 Points per correct answer
                        
                # Update Round 2 Score
                Round2Score.objects.update_or_create(
                    team=team,
                    defaults={
                        'score': score,
                        'completion_time': timezone.localtime(timezone.now()).time()
                    }
                )
                
                return JsonResponse({
                    'success': True,
                    'qualified': True, # Logic for qualification to R3 can be added later
                    'score': score
                })
            else:
                 return JsonResponse({'error': 'Invalid round number'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)

from instructor.models import GameState, Round1Score, Round2Score, Round3Score

def get_game_status(request):
    try:
        game_state = GameState.load()
        active_round = game_state.active_round
        status = game_state.round_status
        
        is_submitted = False
        team_id = request.session.get('user_id')
        
        is_qualified = True
        rank = None
        current_score = 0
        total_score = 100 # Assuming 10 questions x 10 points
        
        if team_id:
            try:
                team = Team.objects.get(id=team_id)
                
                # Check Qualification for Round 2
                if active_round == 2:
                    is_submitted = Round2Score.objects.filter(team=team).exists()
                    # Logic: Top 20 from Round 1
                    # Get all Round 1 scores sorted by score (desc) and time (asc)
                    r1_scores = Round1Score.objects.all().order_by('-score', 'completion_time')
                    
                    # Convert to list to find rank
                    ranked_teams = list(r1_scores)
                    
                    try:
                        # Find the score object for this team
                        my_score_obj = next((s for s in ranked_teams if s.team == team), None)
                        if my_score_obj:
                            rank = ranked_teams.index(my_score_obj) + 1
                            current_score = my_score_obj.score
                            # Qualified if rank <= 20
                            is_qualified = rank <= 20
                        else:
                            is_qualified = False # Didn't play Round 1?
                    except Exception as e:
                        print(f"Error calculating rank: {e}")
                        is_qualified = False

                elif active_round == 1:
                    is_submitted = Round1Score.objects.filter(team=team).exists()
                elif active_round == 3:
                     is_submitted = Round3Score.objects.filter(team=team).exists()
                     
            except Team.DoesNotExist:
                pass
                
        return JsonResponse({
            'active_round': active_round,
            'round_status': status,
            'is_submitted': is_submitted,
            'is_qualified': is_qualified,
            'rank': rank,
            'last_score': current_score,
            'total_score': total_score
        })
    except Exception as e:
        print(f"Game Status Error: {e}")
        return JsonResponse({
            'active_round': 0,
            'round_status': 'WAITING',
            'is_submitted': False
        })
