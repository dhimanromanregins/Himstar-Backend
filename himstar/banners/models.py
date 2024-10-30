from django.db import models

class BannerOrVideo(models.Model):
    BANNER = 'banner'
    VIDEO = 'video'

    MEDIA_TYPE_CHOICES = [
        (BANNER, 'Banner'),
        (VIDEO, 'Video'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default=BANNER
    )
    banner_image = models.ImageField(upload_to='banners/', blank=True, null=True)
    video_file = models.FileField(upload_to='videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Ensure only one of banner_image or video_file is uploaded
        if self.media_type == self.BANNER:
            self.video_file = None
        elif self.media_type == self.VIDEO:
            self.banner_image = None
        super().save(*args, **kwargs)