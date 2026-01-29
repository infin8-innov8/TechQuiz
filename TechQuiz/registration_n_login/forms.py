from django import forms
from .models import Team

class TeamRegistrationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'team_name', 
            'primary_member_name', 'primary_member_email', 'primary_member_phone', 'primary_member_dept', 'primary_member_year',
            'supporting_member_name', 'supporting_member_email', 'supporting_member_phone',
            'supporting_member_dept', 'supporting_member_year'
        ]
        widgets = {
            'team_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Team Name'}),
            'primary_member_dept': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'primary_member_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
            # Primary Member
            'primary_member_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'primary_member_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'primary_member_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            # Supporting Member
            'supporting_member_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'supporting_member_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'supporting_member_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'supporting_member_dept': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
            'supporting_member_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Year'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        primary_email = cleaned_data.get('primary_member_email')
        supporting_email = cleaned_data.get('supporting_member_email')

        # Check Primary Email
        if primary_email:
            if Team.objects.filter(primary_member_email=primary_email).exists() or \
               Team.objects.filter(supporting_member_email=primary_email).exists():
                raise forms.ValidationError(f"The email '{primary_email}' is already registered.")

        # Check Supporting Email
        if supporting_email:
            if Team.objects.filter(primary_member_email=supporting_email).exists() or \
               Team.objects.filter(supporting_member_email=supporting_email).exists():
                raise forms.ValidationError(f"The email '{supporting_email}' is already registered.")
        
        # Check if they are the same
        if primary_email and supporting_email and primary_email == supporting_email:
            raise forms.ValidationError("Primary and Supporting members cannot have the same email.")

        return cleaned_data
