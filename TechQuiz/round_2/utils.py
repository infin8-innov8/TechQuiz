import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
import traceback

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SHEET_ID = '1IghZ1CnPgvlZQCej6ev1oFhyIVKbwdbD71ULY2hA2tM'

def get_round2_questions():
    """
    Fetches questions from the Round 2 Google Sheet.
    Format: question | option 1 | option 2 | option 3 | option 4 | correct option number
    """
    if not os.path.exists('token.json'):
        return []

    try:
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
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
            
            # Robust correct answer parsing (same logic as Round 1)
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
