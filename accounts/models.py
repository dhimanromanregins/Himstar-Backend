from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import datetime
import uuid

class Register(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=255, unique=True, blank=True)
    phonenumber = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,15}$')])
    zipcode = models.CharField(max_length=10)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    dob = models.DateField()
    points = models.BigIntegerField(default=0)
    votes = models.BigIntegerField(default=0)
    cover_image = models.ImageField(upload_to='cover-images/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile-images/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.custom_id:
            unique_id = f"CUS{uuid.uuid4().hex[:8].upper()}"
            while Register.objects.filter(custom_id=unique_id).exists():
                unique_id = f"CUS{uuid.uuid4().hex[:8].upper()}"
            self.custom_id = unique_id
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at).seconds > 300



