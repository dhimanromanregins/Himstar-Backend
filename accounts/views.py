from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, OTPVerifySerializer,LoginSerializer
from .models import Register

# View to handle registration and sending OTP
class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Send OTP
            return Response({"status":status.HTTP_200_OK, "message": "OTP sent successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# View to verify OTP and complete registration
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
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)