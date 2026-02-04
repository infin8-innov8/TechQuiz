import gspread
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os

import traceback

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

from django.conf import settings

def get_questions_from_sheet():
    # ... (start of function)

    """
    Fetches questions from the 'round1questions' Google Sheet.
    Expected Format: question | option 1 | option 2 | option 3 | option 4 | correct option
    Returns a list of dictionaries compatible with the frontend quizData.
    """
    token_path = os.path.join(settings.BASE_DIR, 'token.json')
    
    if not os.path.exists(token_path):
        return []

    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            
        client = gspread.authorize(creds)
        
        # Open the specific sheet
        # Assuming the file name is 'round1questions' or user meant a sheet named that inside a file?
        # Let's try to open a spreadsheet named "round1questions"
        # If it fails, we might need the Spreadsheet ID from the user.
        # For now, trying by name.
        try:
            # Open by Key (ID) explicitly to avoid Drive API scope requirement
            sheet = client.open_by_key("1BGCfQj4p4zRzupIAQy_BWyJPiBodxRgWz4pQsTiTX9k").sheet1
        except gspread.SpreadsheetNotFound:
            print("Spreadsheet not found (check ID/Permissions).")
            return []

        # Get all records
        # Assuming the first row is headers: Question, Option 1, Option 2, Option 3, Option 4, Correct Option
        # Or if no headers, we read all values.
        # User said: "question | option 1 | option 2 | option 3 | option 4 | correct option"
        # Let's assume headers exist or we skip row 1 if it looks like a header.
        
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
            correct_val = row[5].strip() # Could be "Option 1", "1", "A", or the text itself
            
            # Determine correct index (0-3)
            # Common patterns: '1', '2', '3', '4' -> 0, 1, 2, 3
            # 'A', 'B', 'C', 'D' -> 0, 1, 2, 3
            # Or formatted like "Option 1"
            
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
