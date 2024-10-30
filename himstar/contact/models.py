from django.db import models

# Create your models here.

class Contact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.BigIntegerField()
    message = models.TextField()