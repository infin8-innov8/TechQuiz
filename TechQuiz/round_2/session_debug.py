from django.shortcuts import HttpResponse
import random

def session_test(request):
    if 'test_val' not in request.session:
        val = random.randint(1, 1000)
        request.session['test_val'] = val
        return HttpResponse(f"Set session value to: {val}. Refresh to check persistence.")
    else:
        return HttpResponse(f"Session value persists: {request.session['test_val']}")
