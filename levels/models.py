from django.db import models

# Create your models here.

class Stage(models.Model):
    STAGE_CHOICES = [
        ('Bronze', 'Bronze'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
    ]

    name = models.CharField(max_length=50, choices=STAGE_CHOICES, unique=True)
    likes_required = models.PositiveIntegerField()
    award = models.URLField(blank=True, null=True)
    border_design = models.URLField()

    def __str__(self):
        return f"{self.name} - {self.likes_required} Likes Required"

class Level(models.Model):
    current_stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="levels")
    likes = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.popularity.name} - {self.current_stage.name} Stage"