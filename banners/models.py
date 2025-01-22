import os
from django.db import models
from django.core.files.storage import default_storage
from dashboard.models import Category
# import boto3
from botocore.exceptions import NoCredentialsError

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

class BannerOrVideo(models.Model):
    BANNER = 'banner'
    VIDEO = 'video'

    MEDIA_TYPE_CHOICES = [
        (BANNER, 'Banner'),
        (VIDEO, 'Video'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default=BANNER
    )
    banner_image = models.ImageField(upload_to='temp_banners/', blank=True, null=True)
    video_file = models.FileField(upload_to='temp_videos/', blank=True, null=True)
    file_uri = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Ensure only one of banner_image or video_file is uploaded
        if self.media_type == self.BANNER:
            self.video_file = None
        elif self.media_type == self.VIDEO:
            self.banner_image = None

        # Save the object to generate a file path
        super().save(*args, **kwargs)

        # Upload the file to S3
        # if self.media_type == self.BANNER and self.banner_image:
        #     self.upload_to_s3(self.banner_image, 'banners/')
        # elif self.media_type == self.VIDEO and self.video_file:
        #     self.upload_to_s3(self.video_file, 'videos/')

    def upload_to_s3(self, file_field, folder):
        """
        Uploads the given file to the S3 bucket and updates the file field with its URL.
        """
        try:
            file_path = file_field.path  # Local file path
            s3_key = f"{folder}{os.path.basename(file_path)}"  # Destination path in S3
            s3_client.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, s3_key)

            # Generate the S3 file URL
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"

            # Update the field to store the S3 URL instead of the local file path
            file_field.delete(save=False)  # Remove the local file
            if folder == 'banners/':
                self.banner_image = file_url
            elif folder == 'videos/':
                self.video_file = file_url
            self.file_uri = file_url
            super().save(update_fields=['banner_image', 'video_file', 'file_uri'])
            print(f"File successfully uploaded to S3: {file_url}")
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("AWS credentials not available.")
