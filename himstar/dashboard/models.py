from django.db import models
from accounts.models import Register
from django.utils import timezone
from datetime import datetime, timedelta



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    # Assuming you already have a Category model for categorizing competitions
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Competition(models.Model):
    TOURNAMENT = 'tournament'
    COMPETITION = 'competition'

    COMPETITION_TYPE_CHOICES = [
        (TOURNAMENT, 'Tournament'),
        (COMPETITION, 'Competition'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=255, blank=True, null=True)
    registration_open_date = models.DateField()
    registration_close_date = models.DateField()
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    competition_type = models.CharField(
        max_length=100,
        choices=COMPETITION_TYPE_CHOICES,
        default=COMPETITION
    )
    price = models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    banner_image = models.ImageField(upload_to='competition_banners/', blank=True, null=True)
    rules = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    parent_tournament = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='sub_competitions',
        blank=True,
        null=True,
        help_text="Specify the tournament if this is a round/competition within a tournament."
    )

    def __str__(self):
        return self.name

    @property
    def is_tournament(self):
        return self.competition_type == self.TOURNAMENT

    @property
    def has_sub_competitions(self):
        return self.sub_competitions.exists()

class Participant(models.Model):
    competition = models.ForeignKey(Competition, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    video = models.FileField(upload_to='competition_videos/')
    is_qualified_for_next_round = models.BooleanField(default=False)  # For tracking elimination

    def __str__(self):
        return self.name

class Round(models.Model):
    competition = models.ForeignKey(Competition, related_name="rounds", on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    eliminated_percentage = models.PositiveIntegerField(default=20)  # Percentage eliminated after each round
    max_participants = models.PositiveIntegerField()  # Maximum participants for this round

    def __str__(self):
        return f"Round {self.round_number} of {self.competition.name}"

    def eliminate_participants(self):
        # Eliminate a percentage of participants for the current round based on 'eliminated_percentage'
        total_participants = self.competition.participants.count()
        num_to_eliminate = (total_participants * self.eliminated_percentage) // 100
        participants_to_eliminate = self.competition.participants.all()[:num_to_eliminate]  # Just an example elimination strategy

        for participant in participants_to_eliminate:
            participant.is_qualified_for_next_round = False
            participant.save()

class Tournament(models.Model):
    tournament = models.OneToOneField(Competition, related_name='tournament', on_delete=models.CASCADE, limit_choices_to={'competition_type': 'tournament'})
    total_rounds = models.PositiveIntegerField()

    def __str__(self):
        return f"Tournament: {self.tournament.name}"

    def start_next_round(self):
        current_round_number = self.tournament.rounds.count() + 1
        new_round = Round.objects.create(
            competition=self.tournament,
            round_number=current_round_number,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=7),
            max_participants=(self.tournament.max_participants * 80) // 100  # For example, if 20% are eliminated
        )
        new_round.eliminate_participants()


class CompetitionMedia(models.Model):
    VIDEO = 'video'
    SOUND = 'sound'
    MUSIC = 'music'

    MEDIA_TYPE_CHOICES = [
        (VIDEO, 'Video'),
        (SOUND, 'Sound'),
        (MUSIC, 'Music'),
    ]
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='media')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    video_file = models.FileField(upload_to='competition_videos/', blank=True, null=True)
    sound_file = models.FileField(upload_to='competition_sounds/', blank=True, null=True)
    music_file = models.FileField(upload_to='competition_music/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.competition.name} - {self.get_media_type_display()}"

    def save(self, *args, **kwargs):
        if self.media_type == self.VIDEO:
            self.sound_file = None
            self.music_file = None
        elif self.media_type == self.SOUND:
            self.video_file = None
            self.music_file = None
        elif self.media_type == self.MUSIC:
            self.video_file = None
            self.sound_file = None
        super().save(*args, **kwargs)

