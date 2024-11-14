from django.contrib import admin
from .models import Category, Competition, CompetitionMedia, Round, Tournament, Participant
# Register your models here.

admin.site.register(Category)
admin.site.register(Competition)
admin.site.register(CompetitionMedia)
admin.site.register(Round)
admin.site.register(Tournament)
admin.site.register(Participant)
