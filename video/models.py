from django.db import models
from django.contrib.auth import get_user_model
from dashboard.models import Competition, Tournament
from accounts.models import Register
import uuid
# import boto3
from botocore.exceptions import NoCredentialsError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.core.exceptions import ValidationError

import os
User = get_user_model()


# AWS S3 configuration
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
AWS_STORAGE_BUCKET_NAME = ''
AWS_S3_REGION_NAME = ''

# Initialize S3 client
# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_S3_REGION_NAME
# )
s3_client = None

def generate_video_filename(instance, filename):
    extension = filename.split('.')[-1]
    return f"videos/{uuid.uuid4()}.{extension}"

class Participant(models.Model):
    competition = models.ForeignKey(Competition, related_name="participants", on_delete=models.SET_NULL, null=True, blank=True)
    # tournament = models.ForeignKey(Tournament, related_name="tournaments", on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    video = models.FileField(upload_to='competition_participants_videos/', blank=True, null=True)
    # is_qualified_for_next_round = models.BooleanField(default=False)  # For tracking elimination
    file_uri = models.CharField(max_length=255, blank=True, null=True)
    temp_video = models.FileField(upload_to='competition_participants_temp_videos/', blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Upload the file to S3
        # if self.video:
        #     self.upload_to_s3(self.video, 'competition_participants_videos/')

    def upload_to_s3(self, file_field, folder):
        """
        Uploads the given file to the S3 bucket and updates the file field with its URL.
        """
        try:
            if str(file_field).startswith(f"https://{AWS_STORAGE_BUCKET_NAME}.s3"):
                print("File already uploaded to S3. Skipping re-upload.")
                return
            file_path = file_field.path  # Local file path
            s3_key = f"{folder}{os.path.basename(file_path)}"  # Destination path in S3
            s3_client.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, s3_key)

            # Generate the S3 file URL
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"

            # Update the field to store the S3 URL instead of the local file path
            file_field.delete(save=False)  # Remove the local file
            self.video = file_url
            self.file_uri = file_url
            super().save(update_fields=['video', 'file_uri'])
            print(f"File successfully uploaded to S3: {file_url}")
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("AWS credentials not available.")

    def __str__(self):
        return f"{self.user.user.username}"






class Like(models.Model):
    """Model to represent a like on a post."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # A user can like a post only once.

    def __str__(self):
        return f"{self.user.user.username} likes {self.post}"


class Comment(models.Model):
    """Model to represent a comment on a post."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.user.username} on {self.post}"


class Favorite(models.Model):
    """Model to represent a favorite post for a user."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # A user can favorite a post only once.

    def __str__(self):
        return f"{self.user.user.username} favorited {self.post}"


class Share(models.Model):
    """Model to represent a shareable link for a post."""
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='shares')
    post = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='shares')
    share_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.user.username} shared {self.post} with URL {self.share_url}"




