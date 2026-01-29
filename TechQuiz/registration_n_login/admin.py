from django.contrib import admin

from .models import Team

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'team_name', 
        'primary_member_dept', 
        'primary_member_year', 
        'primary_member_name', 
        'primary_member_email',
        'supporting_member_name',
        'supporting_member_email',
        'created_at'
    )
    search_fields = ('team_name', 'primary_member_name', 'primary_member_email')
    list_filter = ('primary_member_dept', 'primary_member_year', 'created_at')
