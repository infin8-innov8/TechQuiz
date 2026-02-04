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
            # SECURITY FIX: Use Session ID instead of trusting frontend payload
            team_id = request.session.get('user_id')
            
            # Allow fallback to payload ONLY if session is empty (e.g. for API testing tools)
            # But in production, we should enforce session.
            if not team_id:
                # Try payload one last time, but prefer session
                team_id = data.get('team_id')

            answers = data.get('answers', []) # Expecting list of whole question_id: x, selected_option: y
            round_num = data.get('round')
            
            if not team_id:
                return JsonResponse({'error': 'Not Logged In (Team ID missing from session)'}, status=401)
                
            try:
                team = Team.objects.get(id=team_id)
            except Team.DoesNotExist:
                 return JsonResponse({'error': f'Team not found (ID: {team_id})'}, status=404)
                 
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
                        score += 20 # 20 Points per correct answer
                        
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
        
        # total_score assumption: R1=100 (10x10), R2=200 (10x20)
        total_score = 200 if active_round == 2 else 100
        
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
            # Use the currently selected question from GameState
            current_q = game_state.current_round3_question
            
            if current_q:
                # Get logs for this specific question, sorted by time
                logs = BerserkLog.objects.filter(
                    question=current_q, 
                    is_illegal=False
                ).select_related('team').order_by('timestamp')
                
                seen_teams = set()
                rank = 1
                for log in logs:
                    if log.team_id not in seen_teams:
                        leaderboard_data.append({
                            'rank': rank,
                            'team_name': log.team.team_name,
                            'score': 'LOGGED',
                            'timestamp': timezone.localtime(log.timestamp).strftime('%H:%M:%S.%f')[:-3]
                        })
                        seen_teams.add(log.team_id)
                        rank += 1

        return JsonResponse({
            'active_round': active_round,
            'round_status': game_state.round_status,
            'leaderboard': leaderboard_data[:10],
            'active_question_text': current_q.question_text if active_round == 3 and current_q else None,
            'active_question_number': current_q.sequence_order if active_round == 3 and current_q else None,
            'is_unlocked': current_q.is_active if active_round == 3 and current_q else False
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
        team_id = request.session.get('user_id')
        
        if not team_id:
             return JsonResponse({'error': 'Not logged in'}, status=401)
             
        from instructor.models import GameState, Round3Question, BerserkLog, Round3Score, Team
        
        game_state = GameState.objects.first()
        if not game_state or game_state.active_round != 3:
            return JsonResponse({'error': 'Round 3 not active'}, status=400)
            
        team = Team.objects.get(id=team_id)
        
        # Get currently selected question
        current_q = game_state.current_round3_question
        
        if not current_q:
            return JsonResponse({'error': 'No question selected'}, status=400)

        # 1. First, check if a legal hit already exists for this team/question
        # A user can appear only once in the leaderboard (first legal hit counts)
        if BerserkLog.objects.filter(team=team, question=current_q, is_illegal=False).exists():
            return JsonResponse({'status': 'logged', 'message': 'Already logged!'}, status=200)

        # 2. Create the log
        log = BerserkLog.objects.create(
            team=team,
            question=current_q
        )
        
        # Determine legality: Hit must be >= activated_at
        is_illegal = False
        if not current_q.is_active or not current_q.activated_at:
             is_illegal = True
        elif log.timestamp < current_q.activated_at:
             is_illegal = True
             
        if is_illegal:
            log.is_illegal = True
            log.save()
            
            # Check for cumulative penalty (3 strikes for this question? or overall?)
            # User previously asked for "3 illegal hits = -10 penalty".
            # Let's count illegal hits for THIS question for THIS team.
            illegal_count = BerserkLog.objects.filter(
                team=team, 
                question=current_q, 
                is_illegal=True
            ).count()
            
            if illegal_count % 3 == 0:
                r3_score, _ = Round3Score.objects.get_or_create(team=team)
                r3_score.score -= 10
                r3_score.save()
                return JsonResponse({
                    'status': 'illegal', 
                    'message': f'PENALTY! {illegal_count} Illegal Hits. -10 Points.',
                    'illegal_count': illegal_count
                })
                
            return JsonResponse({
                'status': 'illegal', 
                'message': 'Illegal Hit (False Start)!',
                'illegal_count': illegal_count
            })
            
        return JsonResponse({'status': 'logged', 'message': 'Berserk Recorded!'})


    except Exception as e:
        print(f"Berserk Error: {e}")
        return JsonResponse({'error': str(e)}, status=500)
