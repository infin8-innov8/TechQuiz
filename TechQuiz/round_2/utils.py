import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import traceback

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1IghZ1CnPgvlZQCej6ev1oFhyIVKbwdbD71ULY2hA2tM'

from django.conf import settings

import sys

def get_round2_questions():
    """
    Fetches questions from the Round 2 Google Sheet.
    Format: question | option 1 | option 2 | option 3 | option 4 | correct option number
    """
    try:
        # Service Account Path
        service_account_path = os.path.join(settings.BASE_DIR, 'service_account.json')
        client = None
        
        if os.path.exists(service_account_path):
            try:
                client = gspread.service_account(filename=service_account_path)
                sys.stderr.write(f"DEBUG: Authenticated with Service Account at {service_account_path}\n")
            except Exception as e:
                sys.stderr.write(f"DEBUG: Service Account auth failed: {e}\n")
                client = None
        
        if not client:
            # Robust Path Finding for fallback token.json
            potential_paths = [
                os.path.join(settings.BASE_DIR, 'token.json'),
                os.path.join(settings.BASE_DIR, 'TechQuiz', 'token.json'), 
                os.path.join(os.getcwd(), 'token.json'),
            ]

            token_path = None
            for path in potential_paths:
                if os.path.exists(path):
                    token_path = path
                    break
                    
            if not token_path:
                sys.stderr.write("DEBUG: token.json NOT FOUND and service_account.json missing in Round 2!\n")
                return []

            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                
            client = gspread.authorize(creds)
        
        try:
            sheet = client.open_by_key(SHEET_ID).sheet1
        except gspread.SpreadsheetNotFound:
            print("Round 2 Spreadsheet not found.")
            return []

        rows = sheet.get_all_values()
        if not rows:
            return []
            
        # Check header
        if rows[0][0].lower().startswith('question'):
            rows = rows[1:]

        questions = []
        for index, row in enumerate(rows):
            if len(row) < 6:
                continue
                
            question_text = row[0]
            options = [row[1], row[2], row[3], row[4]]
            
            # Robust correct answer parsing
            correct_val = row[5].strip()
            correct_idx = 0
            
            if correct_val.isdigit():
                correct_idx = int(correct_val) - 1
            elif len(correct_val) == 1 and correct_val.upper() in ['A', 'B', 'C', 'D']:
                correct_idx = ord(correct_val.upper()) - 65
            elif correct_val.lower().startswith("option"):
                 try:
                     correct_idx = int(correct_val.split()[-1]) - 1
                 except: 
                     pass
            else:
                try:
                    correct_idx = options.index(correct_val)
                except ValueError:
                    correct_idx = 0 
            
            # Clamp index
            correct_idx = max(0, min(correct_idx, 3))

            questions.append({
                "id": index + 1,
                "q": question_text,
                "options": options,
                "correct": correct_idx
            })
            
        return questions

    except Exception as e:
        print("Error fetching Round 2 questions:")
        traceback.print_exc()
        return []
