from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
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
                f"Greetings from the Tech Innovation & Creativity Club (TIC)!\n\n"
                f"We are pleased to inform you that your registration for the TechQuiz Competition has been successfully confirmed. 🎉\n"
                f"Thank you for showing enthusiasm and interest in participating—your curiosity and competitive spirit are exactly what "
                f"TechQuiz is designed to celebrate.\n\n"
                f"To ensure smooth communication regarding competition updates, schedules, rules, and announcements, "
                f"all registered teams are required to join the official TechQuiz WhatsApp Channel using the link provided below:\n\n"
                f"🔗 WhatsApp Channel Link: https://chat.whatsapp.com/J6EoNG9UOEN9G5H0mY4USg\n\n"
                f"Please make sure that at least one team representative joins the channel at the earliest to avoid missing any important information.\n\n"
                f"If you have any queries or require assistance, feel free to reach out to us through the WhatsApp channel or contact the TIC coordinators.\n\n"
                f"We look forward to your active participation and wish Team {team.team_name} the very best for the competition.\n\n"
                f"For querries, contact to pranav.vasankar@gmail.com or call on 7387 47 7279\n\n"
                f"Warm regards,\n"
                f"Team TIC\n"
                f"Tech Innovation & Creativity Club\n"
                f"Innovate | Compete | Create"
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
        
    return render(request, 'register/register.html', {'form': form})

def success(request):
    return render(request, 'register/success.html')
