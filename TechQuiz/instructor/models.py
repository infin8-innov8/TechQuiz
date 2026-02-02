from django.db import models
from registration_n_login.models import Team

class GameState(models.Model):
    ROUND_CHOICES = [
        (1, 'Round 1'),
        (2, 'Round 2'),
        (3, 'Round 3 (Physical)'),
    ]
    STATUS_CHOICES = [
        ('WAITING', 'Waiting'),
        ('ONGOING', 'Ongoing'),
        ('DONE', 'Done'),
    ]

    active_round = models.IntegerField(choices=ROUND_CHOICES, default=1)
    round_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAITING')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and GameState.objects.exists():
            # If you're trying to create a new one but one exists, prevent it
            raise ImportError('There can be only one GameState instance')
        return super(GameState, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Round {self.active_round} - {self.round_status}"

class Round1Score(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='r1_score')
    score = models.IntegerField(default=0)
    completion_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.team.team_name} - {self.score}"

class Round2Score(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='r2_score')
    score = models.IntegerField(default=0)
    completion_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.team.team_name} - {self.score}"

class Round3Score(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='r3_score')
    score = models.IntegerField(default=0)
    completion_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.team.team_name} - {self.score}"

class Round3Question(models.Model):
    question_text = models.CharField(max_length=255)
    sequence_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Q{self.sequence_order}: {self.question_text} ({'Active' if self.is_active else 'Locked'})"

class BerserkLog(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='berserk_logs')
    question = models.ForeignKey(Round3Question, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_illegal = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.team.team_name} - {'ILLEGAL' if self.is_illegal else 'VALID'} - {self.timestamp.strftime('%H:%M:%S.%f')}"
