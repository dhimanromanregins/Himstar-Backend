from django.db import models
from django.contrib.auth import get_user_model
from dashboard.models import Competition
from accounts.models import Register
import uuid
User = get_user_model()


def generate_video_filename(instance, filename):
    extension = filename.split('.')[-1]
    return f"videos/{uuid.uuid4()}.{extension}"

class Post(models.Model):
    """Model for user posts, with support for video uploads."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='posts')
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='competition')
    caption = models.TextField(blank=True, null=True)
    video = models.FileField(upload_to=generate_video_filename, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_likes(self):
        return self.likes.count()

    def total_comments(self):
        return self.comments.count()


class Like(models.Model):
    """Model to represent a like on a post."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # A user can like a post only once.

    def __str__(self):
        return f"{self.user.user.username} likes {self.post}"


class Comment(models.Model):
    """Model to represent a comment on a post."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.user.username} on {self.post}"


class Favorite(models.Model):
    """Model to represent a favorite post for a user."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # A user can favorite a post only once.

    def __str__(self):
        return f"{self.user.user.username} favorited {self.post}"


class Share(models.Model):
    """Model to represent a shareable link for a post."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='shares')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='shares')
    share_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} shared {self.post} with URL {self.share_url}"
