from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Contact
from .serializers import ContactSerializer

class ContactCreateView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the contact information to the database
            return Response({ "status":status.HTTP_201_CREATED,"message": "Contact information submitted successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
