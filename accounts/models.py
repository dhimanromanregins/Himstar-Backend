from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
import datetime
import uuid

class Register(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    custom_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    phonenumber = models.CharField(max_length=15, validators=[RegexValidator(r'^\d{10,15}$')], null=True, blank=True)
    zipcode = models.CharField(max_length=10,null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    points = models.BigIntegerField(default=0)
    votes = models.BigIntegerField(default=0)
    cover_image = models.ImageField(upload_to='cover-images/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile-images/', blank=True, null=True)
    referral_code = models.CharField(max_length=100, unique=True, null=True)

    def save(self, *args, **kwargs):
        if not self.custom_id:
            unique_id = f"CUS{uuid.uuid4().hex[:8].upper()}"
            referral_code = f"REF{uuid.uuid4().hex[:8].upper()}"
            while Register.objects.filter(custom_id=unique_id).exists():
                unique_id = f"CUS{uuid.uuid4().hex[:8].upper()}"
            while Register.objects.filter(referral_code=referral_code).exists():
                referral_code = f"REF{uuid.uuid4().hex[:8].upper()}"
            self.custom_id = unique_id
            self.referral_code = referral_code
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Referral(models.Model):
    inviter = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='referrals_made')
    invitee = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='referred_by')
    referral_code = models.CharField(max_length=100)
    date_referred = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed')],
                              default='pending')

    def __str__(self):
        return f"Referral: {self.inviter} -> {self.invitee} ({self.status})"

class ReferralReward(models.Model):
    amount = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Referral Reward: Rs.{self.amount}"

class OTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (datetime.datetime.now(datetime.timezone.utc) - self.created_at).seconds > 30000
    

class Awards(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="awards")
    votes_required = models.CharField(max_length=255)




