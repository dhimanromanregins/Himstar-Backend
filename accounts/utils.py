import random
from django.core.mail import send_mail
from django.conf import settings

# Function to generate a 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Function to send OTP via email
def send_otp(email, otp):
    subject = "Your OTP for Registration"
    print(otp, '==================')
    message = f"Your OTP for registration is {otp}. Please use this to complete your registration."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)