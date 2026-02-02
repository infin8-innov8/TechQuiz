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
        
        team_name = ""
        if team_id:
            try:
                team = Team.objects.get(id=team_id)
                team_name = team.team_name
                
                # Check Qualification for Round 2
                if active_round == 2:
                    is_submitted = Round2Score.objects.filter(team=team).exists()
                    # Logic: Top 20 from Round 1
                    r1_scores = Round1Score.objects.all().order_by('-score', 'completion_time')
                    ranked_teams = list(r1_scores)
                    
                    try:
                        my_score_obj = next((s for s in ranked_teams if s.team == team), None)
                        if my_score_obj:
                            rank = ranked_teams.index(my_score_obj) + 1
                            current_score = my_score_obj.score
                            # Qualified if rank <= 20
                            is_qualified = rank <= 20
                        else:
                            is_qualified = False 
                    except Exception as e:
                        print(f"Error calculating rank R2: {e}")
                        is_qualified = False

                # Check Qualification for Round 3
                elif active_round == 3:
                    # Logic: Top 10 from Round 2
                    is_submitted = False # Round 3 is live, never "submitted" in the traditional sense
                    
                    r2_scores = Round2Score.objects.all().order_by('-score', 'completion_time')
                    ranked_teams_r2 = list(r2_scores)
                    
                    try:
                         my_score_obj = next((s for s in ranked_teams_r2 if s.team == team), None)
                         if my_score_obj:
                             rank = ranked_teams_r2.index(my_score_obj) + 1
                             current_score = my_score_obj.score
                             # Qualified if rank <= 10
                             is_qualified = rank <= 10
                         else:
                             # If they didn't play Round 2, they can't be in Round 3
                             is_qualified = False
                    except Exception as e:
                        print(f"Error calculating rank R3: {e}")
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
            'total_score': total_score,
            'team_name': team_name
        })
    except Exception as e:
        print(f"Game Status Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def get_leaderboard(request):
    try:
        from instructor.models import GameState, Round1Score, Round2Score
        
        # Get active round
        game_state = GameState.objects.first()
        if not game_state:
            return JsonResponse({'error': 'Game State not initialized'}, status=400)
            
        active_round = game_state.active_round
        
        leaderboard_data = []
        
        if active_round == 1:
            # Rank R1: Score Desc, Time Asc
            scores = Round1Score.objects.select_related('team').order_by('-score', 'completion_time')
            for idx, s in enumerate(scores, 1):
                leaderboard_data.append({
                    'rank': idx,
                    'team_name': s.team.team_name,
                    'score': s.score,
                    'timestamp': s.completion_time.strftime('%H:%M:%S.%f')[:-3] if s.completion_time else "N/A"
                })
                
        elif active_round == 2:
            # Rank R2: Score Desc, Time Asc
            scores = Round2Score.objects.select_related('team').order_by('-score', 'completion_time')
            for idx, s in enumerate(scores, 1):
                leaderboard_data.append({
                    'rank': idx,
                    'team_name': s.team.team_name,
                    'score': s.score,
                    'timestamp': s.completion_time.strftime('%H:%M:%S.%f')[:-3] if s.completion_time else "N/A"
                })
        
        elif active_round == 3:
            from instructor.models import Round3Question, BerserkLog
            # Find active question
            active_q = Round3Question.objects.filter(is_active=True).first()
            
            if active_q:
                # Get valid logs for this question, sorted by time (first finger first)
                logs = BerserkLog.objects.filter(
                    question=active_q, 
                    is_illegal=False
                ).select_related('team').order_by('timestamp')
                
                for idx, log in enumerate(logs, 1):
                    leaderboard_data.append({
                        'rank': idx,
                        'team_name': log.team.team_name,
                        'score': 'LOGGED', # No score yet, just order
                        'timestamp': log.timestamp.strftime('%H:%M:%S.%f')[:-3]
                    })
            else:
                # If no active question, maybe show overall Round 3 scores?
                # For now, return empty or last question's logs?
                pass

        return JsonResponse({
            'active_round': active_round,
            'round_status': game_state.round_status,
            'leaderboard': leaderboard_data[:10]  # Top 10 only
        })

    except Exception as e:
        print(f"Leaderboard Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def berserk_click(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        data = json.loads(request.body)
        team_id = request.session.get('team_id')
        
        if not team_id:
             return JsonResponse({'error': 'Not logged in'}, status=401)
             
        from instructor.models import GameState, Round3Question, BerserkLog, Round3Score, Team
        
        game_state = GameState.objects.first()
        if not game_state or game_state.active_round != 3:
            return JsonResponse({'error': 'Round 3 not active'}, status=400)
            
        team = Team.objects.get(id=team_id)
        
        # Check for active question
        active_q = Round3Question.objects.filter(is_active=True).first()
        
        if active_q:
            # VALID HIT
            # Log it
            BerserkLog.objects.create(
                team=team,
                question=active_q,
                is_illegal=False
            )
            return JsonResponse({'status': 'logged', 'message': 'Berserk Recorded!'})
            
        else:
            # ILLEGAL HIT
            BerserkLog.objects.create(
                team=team,
                question=None, # No active question
                is_illegal=True
            )
            
            # Check penalty (3rd illegal hit = -10)
            illegal_count = BerserkLog.objects.filter(team=team, is_illegal=True).count()
            
            if illegal_count % 3 == 0:
                # Penalty
                score_obj, created = Round3Score.objects.get_or_create(team=team)
                score_obj.score -= 10
                score_obj.save()
                return JsonResponse({'status': 'penalty', 'message': 'ILLEGAL HIT! -10 Points Penalty!'})
            
            return JsonResponse({'status': 'illegal', 'message': f'Illegal Hit! Warning {illegal_count % 3}/3'})

    except Exception as e:
        print(f"Berserk Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
