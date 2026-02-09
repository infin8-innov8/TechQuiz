import os
import django
from django.conf import settings

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TechQuiz.settings')
django.setup()

from round_2.utils import get_round2_questions

try:
    print("Fetching Round 2 questions...")
    questions = get_round2_questions()
    print(f"Found {len(questions)} questions.")
    for i, q in enumerate(questions):
        print(f"[{i+1}] Q: '{q['q']}'")
        print(f"     Options: {q['options']}")
        print(f"     Correct: {q['correct']}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
