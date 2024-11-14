from django.contrib import admin
from .models import Post, Favorite, Like, Comment, Share
# Register your models here.
admin.site.register(Post)
admin.site.register(Favorite)
admin.site.register(Like)
admin.site.register(Comment)
admin.site.register(Share)
