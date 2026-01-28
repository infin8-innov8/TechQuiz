from django.db import models

class Team(models.Model):
    team_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    year = models.CharField(max_length=20)
    
    # Primary Member
    primary_member_name = models.CharField(max_length=100)
    primary_member_email = models.EmailField()
    primary_member_phone = models.CharField(max_length=15, blank=True, null=True)
    
    # Supporting Member
    supporting_member_name = models.CharField(max_length=100)
    supporting_member_email = models.EmailField()
    supporting_member_phone = models.CharField(max_length=15, blank=True, null=True)
    supporting_member_dept = models.CharField(max_length=100, blank=True, null=True)
    supporting_member_year = models.CharField(max_length=20, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.team_name
