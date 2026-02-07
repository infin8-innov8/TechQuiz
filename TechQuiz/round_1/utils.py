import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os

import traceback

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

from django.conf import settings

import sys

def get_questions_from_sheet():
    """
    Fetches questions from the 'round1questions' Google Sheet.
    Expected Format: question | option 1 | option 2 | option 3 | option 4 | correct option
    Returns a list of dictionaries compatible with the frontend quizData.
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
            # Fallback to User Auth (Token.json)
            potential_paths = [
                os.path.join(settings.BASE_DIR, 'token.json'),
                os.path.join(settings.BASE_DIR, 'TechQuiz', 'token.json'), # Check inner folder explicitly
                os.path.join(os.getcwd(), 'token.json'),
            ]

            token_path = None
            for path in potential_paths:
                sys.stderr.write(f"DEBUG: Checking path: {path}\n")
                if os.path.exists(path):
                    token_path = path
                    sys.stderr.write(f"DEBUG: FOUND token.json at {token_path}!\n")
                    break
                    
            if not token_path:
                sys.stderr.write("DEBUG: token.json NOT FOUND in any expected location and service_account.json missing!\n")
                return []

            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                
            client = gspread.authorize(creds)
        
        # Open the specific sheet
        try:
            # Open by Key (ID) explicitly to avoid Drive API scope requirement
            sheet = client.open_by_key("1BGCfQj4p4zRzupIAQy_BWyJPiBodxRgWz4pQsTiTX9k").sheet1
        except gspread.SpreadsheetNotFound:
            print("Spreadsheet not found (check ID/Permissions).")
            return []

        # Get all records
        rows = sheet.get_all_values()
        if not rows:
            return []
            
        # Check if first row is header
        if rows[0][0].lower() == 'question':
            rows = rows[1:]

        questions = []
        for index, row in enumerate(rows):
            if len(row) < 6:
                continue
                
            question_text = row[0]
            options = [row[1], row[2], row[3], row[4]]
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
                # Try to find exact text match
                try:
                    correct_idx = options.index(correct_val)
                except ValueError:
                    correct_idx = 0 # Default fallback
            
            questions.append({
                "id": index + 1,
                "q": question_text,
                "options": options,
                "correct": correct_idx
            })
            
        return questions

    except Exception as e:
        print("Error fetching questions:")
        traceback.print_exc()
        return []
