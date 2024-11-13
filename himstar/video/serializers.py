# serializers.py
from rest_framework import serializers
from .models import Post, Like, Comment, Favorite, Share

class PostSerializer(serializers.ModelSerializer):
    total_likes = serializers.IntegerField(source='total_likes', read_only=True)
    total_comments = serializers.IntegerField(source='total_comments', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'caption', 'video', 'created_at', 'total_likes', 'total_comments']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'share_url', 'created_at']
