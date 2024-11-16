import os
from django.db import models
import boto3
from botocore.exceptions import NoCredentialsError

# AWS S3 configuration
AWS_ACCESS_KEY_ID = 'AKIAZI2LC6I47KFGTHPJ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'himstar'
AWS_S3_REGION_NAME = 'us-east-2'

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_S3_REGION_NAME
)


class UploadedFile(models.Model):
    file = models.FileField(upload_to='temp_uploads/')  # Temporary local upload
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

    def save(self, *args, **kwargs):
        # Save the object to generate a file path
        super().save(*args, **kwargs)

        # Upload the file to S3
        if self.file:
            self.upload_to_s3()

    def upload_to_s3(self):
        """
        Uploads the file to the S3 bucket and updates the file field with its URL.
        """
        try:
            file_path = self.file.path  # Local file path
            s3_key = f"uploads/{os.path.basename(file_path)}"  # Destination path in S3
            s3_client.upload_file(file_path, AWS_STORAGE_BUCKET_NAME, s3_key)

            # Generate the S3 file URL
            file_url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"

            # Update the field to store the S3 URL instead of the local file path
            self.file.delete(save=False)  # Remove the local file
            self.file = file_url
            super().save(update_fields=['file'])

            print(f"File successfully uploaded to S3: {file_url}")
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("AWS credentials not available.")
