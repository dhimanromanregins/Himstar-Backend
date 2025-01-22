from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import BannerOrVideo
from dashboard.models import Category
from .serializers import BannerOrVideoSerializer
from rest_framework.permissions import IsAuthenticated



class BannersByCategoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            banners = BannerOrVideo.objects.all()

            # Serialize the data
            serializer = BannerOrVideoSerializer(banners, many=True)

            # Return a JSON response with serialized data
            return Response({
                'banners': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Generic exception handler for other unexpected errors
            return Response(
                {'error': 'An error occurred while retrieving banners.', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )