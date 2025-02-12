from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, OTPVerifySerializer,LoginSerializer,AwardsSerializer, RegisterSerializerPasswordUpdate, ReferralHistorySerializer
from .models import Register, Awards, OTP, Referral
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .utils import verify_google_token
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_otp, send_otp
import requests
from django.core.files.base import ContentFile

# View to handle registration and sending OTP
class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        print('request.data>>>', request.data)
        if User.objects.filter(username=request.data['username']).exists():
            return Response({"username": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=request.data['email']).exists():
            return Response({"email": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if Register.objects.filter(phonenumber=request.data['phonenumber']).exists():
            return Response({"phonenumber": "Phone number already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.data['password'] != request.data['confirm_password']:
            return Response({"password": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        ref_code = request.data.get('ref_code')
        if ref_code:
            if len(ref_code) != 11 or ref_code[:3] != 'REF':
                return Response({"error": "Invalid referral code format."}, status=status.HTTP_400_BAD_REQUEST)
            inviter = Register.objects.filter(referral_code=ref_code).first()
            if not inviter:
                return Response({"error": "Referral code does not exist or is invalid."}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = generate_otp()
        OTP.objects.update_or_create(email=request.data['email'], defaults={'otp': otp_code})
        send_otp(request.data['email'], otp_code)

        return Response({"status":status.HTTP_200_OK, "message": "OTP sent successfully"}, status=status.HTTP_200_OK)

class RegisterDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        username = request.GET.get('username')
        if username:
            register = Register.objects.filter(user__username=username).first()
        else:    
            register = Register.objects.filter(user__id=request.user.id).first()

        if not register:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = RegisterSerializer(register, context={'user_id': register.id})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def patch(self, request):
        user_id = request.user.id
        register = get_object_or_404(Register, user_id=user_id)
        password = request.data.get('password')
        if password:
            register.user.set_password(password)
        print(request.data)

        # update user name
        fname = request.data.get('first_name')
        lname = request.data.get('last_name')
        if fname:
            register.user.first_name = fname
        if lname:
            register.user.last_name = lname

        serializer = RegisterSerializerPasswordUpdate(register, data=request.data, partial=True)
        if serializer.is_valid():
            register.user.save()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPAndRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        otp_data = {
            "email": request.data.get('email'),
            "otp": request.data.get('otp')
        }
        user_data = request.data.get('user_data')  # user_data contains the original user data

        otp_serializer = OTPVerifySerializer(data=otp_data, context={'user_data': user_data})
        if otp_serializer.is_valid():
            otp_serializer.save()  # Register the user
            return Response({"status":status.HTTP_200_OK, "message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(otp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            tokens = serializer.get_tokens(user)
            register = Register.objects.filter(user__id=user.id).first()
            return Response({
                "status":status.HTTP_200_OK,
                'refresh': tokens['refresh'],
                'access': tokens['access'],
                'user_id': user.id,
                'reg_user_id': register.id,
                'username': user.username,
                'email': user.email,
                'phone': register.phonenumber,
                'name': f'{user.first_name} {user.last_name}',
                'profile_image': register.profile_image_url,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AwardsAPIView(APIView):
    def get(self, request):
        awards = Awards.objects.all()
        serializer = AwardsSerializer(awards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AwardsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class GoogleLoginView(APIView):
    def post(self, request, *args, **kwargs):
        google_token = request.data.get('token')  # Token sent by the frontend

        # Verify the Google token
        try:
            google_data = verify_google_token(google_token)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the domain from the email to create the username
        username = google_data['email'].split('@')[0]

        # Check if the user exists by email, and create the user if not
        user, created = User.objects.get_or_create(
            email=google_data['email'],
            defaults={'username': username, 'first_name': google_data['given_name'], 'last_name': google_data['family_name']}
        )

        # Create or update the Register model
        register, created = Register.objects.get_or_create(user=user)
        
        # download profile picture
        if google_data.get('picture'):
            try:
                response = requests.get(google_data['picture'])
                if response.status_code == 200 and created:
                    file_name = f"{username}_profile.jpg"
                    register.profile_image.save(file_name, ContentFile(response.content), save=True)
            except Exception as e:
                print("Error downloading profile image:", e)
        

        # if created:
        #     register.profile_image = google_data.get('picture')  # Save the profile image URL
        #     register.save()

        # Generate access and refresh tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "status": status.HTTP_200_OK,
            'refresh': str(refresh),
            'access': access_token,
            'user_id': user.id,
            'reg_user_id': register.id,
            'username': user.username,
            'email': user.email,
            'phone': register.phonenumber,
            'name': f'{user.first_name} {user.last_name}',
            'profile_image': register.profile_image_url,
        })

class ReferralHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = Register.objects.filter(user=request.user).first()
        referrals = Referral.objects.filter(inviter=user)
        serializer = ReferralHistorySerializer(referrals, many=True)
        return Response({"referral_history": serializer.data, "referrel_code": user.referral_code}, status=status.HTTP_200_OK)
