from django.contrib import admin
from .models import BannerOrVideo

@admin.register(BannerOrVideo)
class BannerOrVideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'created_at')
    list_filter = ('media_type',)