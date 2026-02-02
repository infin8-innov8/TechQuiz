from django.shortcuts import render, redirect, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Team
from .forms import TeamRegistrationForm

def register(request):
    if request.method == 'POST':
        form = TeamRegistrationForm(request.POST)
        if form.is_valid():
            team = form.save()
            
            # Send Email
            subject = 'TechQuiz: Team Registration Successful'
            message = (
                f"Dear Team {team.team_name},\n\n"
                f"Greetings from the Tech Innovation & Creativity Club!\n\n"
                f"We are pleased to inform you that your registration for the TechQuiz Competition has been successfully confirmed. 🎉\n"
                f"Thank you for showing enthusiasm and interest in participating—your curiosity and competitive spirit are exactly what "
                f"TechQuiz is designed to celebrate.\n\n"
                f"To ensure smooth communication regarding competition updates, schedules, rules, and announcements, "
                f"all registered teams are required to join the official TechQuiz WhatsApp Channel using the link provided below:\n\n"
                f"🔗 WhatsApp Channel Link: https://chat.whatsapp.com/J6EoNG9UOEN9G5H0mY4USg\n\n"
                f"Please make sure that at least one team representative joins the channel at the earliest to avoid missing any important information.\n\n"
                f"If you have any queries or require assistance, feel free to reach out to us through the WhatsApp channel or contact to 7387 47 7279.\n\n"
                f"We look forward to your active participation and wish Team {team.team_name} the very best for the competition.\n\n"
                f"Warm regards,\n"
                f"Tech Innovation and Creativity Club\n"
            )
            recipient_list = [team.primary_member_email, team.supporting_member_email]
            
            try:
                send_mail(
                    subject, 
                    message, 
                    settings.EMAIL_HOST_USER, 
                    recipient_list, 
                    fail_silently=False
                )
            except Exception as e:
                print(f"Error sending email: {e}")
                # You might want to log this but usually we still show success page

            return redirect('success')
    else:
        form = TeamRegistrationForm()
        
    return render(request, 'registration_n_login/register.html', {'form': form})

def success(request):
    return render(request, 'registration_n_login/success.html')

import random
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        # Check if email exists as primary member
        try:
            team = Team.objects.get(primary_member_email__iexact=email)
        except Team.DoesNotExist:
            return render(request, 'registration_n_login/login.html', {'message': 'Email not registered as Primary Member.', 'email': email})
            
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store in session
        request.session['auth_otp'] = otp
        request.session['auth_email'] = email
        
        # Send Email
        send_mail(
            'TechQuiz Login OTP',
            f'Your OTP for TechQuiz Login is: {otp}',
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
        
        return redirect('verify_otp')
        
    return render(request, 'registration_n_login/login.html')

def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        session_otp = request.session.get('auth_otp')
        
        if user_otp == session_otp:
            # Login Success
            email = request.session.get('auth_email')
            team = Team.objects.get(primary_member_email=email)
            
            # Set session/cookie for logged in state
            request.session['user_id'] = team.id
            request.session['is_authenticated'] = True
            
            # Clear OTP
            del request.session['auth_otp']
            
            return redirect('waiting_room')
        else:
            return render(request, 'registration_n_login/verify_otp.html', {'message': 'Invalid OTP'})
            
    return render(request, 'registration_n_login/verify_otp.html')

def waiting_room(request):
    team_id = request.session.get('user_id')
    return render(request, 'registration_n_login/waiting_room.html', {'team_id': team_id})
