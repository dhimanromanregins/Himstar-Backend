# serializers.py
from rest_framework import serializers
from .models import Post, Like, Comment, Favorite, Share
from accounts.models import Register


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'user', 'competition', 'caption', 'video', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        likes = Like.objects.filter(post=instance.id).count()
        comments = Comment.objects.filter(post=instance.id).count()

        user_id = self.context.get('user_id')
        is_like = Like.objects.filter(post=instance.id, user=user_id).first()

        representation = super().to_representation(instance)
        representation['username'] = instance.user.user.username
        representation['profile_pic'] = instance.user.profile_pic if instance.user.profile_pic else None
        representation['is_like'] = True if is_like else False
        representation['likes'] = likes
        representation['comments'] = comments
        return representation


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username'] = instance.user.user.username
        representation['profile_pic'] = instance.user.profile_pic if instance.user.profile_pic else None
        return representation


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'created_at']
        read_only_fields = ['created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['username'] = instance.user.user.username
        representation['profile_pic'] = instance.user.profile_pic if instance.user.profile_pic else None
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'post', 'created_at']


class ShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = Share
        fields = ['id', 'user', 'post', 'share_url', 'created_at']
