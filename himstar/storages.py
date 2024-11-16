# settings.py

from storages.backends.s3boto3 import S3Boto3Storage

# Custom storage for static files
class S3StaticStorage(S3Boto3Storage):
    bucket_name = 'your_bucket_name'  # Replace with your bucket name
    custom_domain = 'your_bucket_name.s3.amazonaws.com'  # Replace with your custom domain
    location = 'static'  # Folder in S3 for static files

# Custom storage for media files
class S3MediaStorage(S3Boto3Storage):
    bucket_name = 'your_bucket_name'  # Replace with your bucket name
    custom_domain = 'your_bucket_name.s3.amazonaws.com'  # Replace with your custom domain
    location = 'media'  # Folder in S3 for media files
