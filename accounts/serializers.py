from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Register, OTP
from .utils import generate_otp, send_otp
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):
    phonenumber = serializers.CharField(required=True)
    zipcode = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=True)
    dob = serializers.DateField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'phonenumber', 'zipcode', 'gender', 'dob', 'password', 'confirm_password']

    def validate(self, data):
        # Check if username already exists
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})

        # Check if email already exists
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})

        # Check if phone number already exists
        if Register.objects.filter(phonenumber=data['phonenumber']).exists():
            raise serializers.ValidationError({"phonenumber": "Phone number already exists"})

        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def create(self, validated_data):
        email = validated_data['email']

        # Generate OTP and store it in the OTP model
        otp_code = generate_otp()
        OTP.objects.update_or_create(email=email, defaults={'otp': otp_code})

        # Send OTP to the user's email
        send_otp(email, otp_code)

        return validated_data


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data['email']
        otp = generate_otp()

        # Create or update OTP
        OTP.objects.update_or_create(email=email, defaults={'otp': otp})

        # Send the OTP to the user's email
        send_otp(email, otp)

        return validated_data


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data['email']
        otp = data['otp']

        # Check if the OTP is valid
        try:
            otp_record = OTP.objects.get(email=email, otp=otp)
            if otp_record.is_expired():
                raise serializers.ValidationError("OTP has expired.")
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        return data

    def create(self, validated_data):
        email = validated_data['email']

        # Fetch user data from the context (passed from the view)
        user_data = self.context['user_data']

        # Create the user
        user = User.objects.create_user(
            username=user_data['username'],
            email=email,
            password=user_data['password']
        )

        # Create Register
        Register.objects.create(
            user=user,
            phonenumber=user_data['phonenumber'],
            zipcode=user_data['zipcode'],
            gender=user_data['gender'],
            dob=user_data['dob']
        )

        # OTP verified and user registered
        return user

class LoginSerializer(serializers.Serializer):
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username_or_email = data.get("username_or_email")
        password = data.get("password")

        user = authenticate(username=username_or_email, password=password)
        if not user:
            # Try by email if no user with that username exists
            user_model = User.objects.filter(email=username_or_email).first()
            if user_model:
                user = authenticate(username=user_model.username, password=password)

        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

    def get_tokens(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }