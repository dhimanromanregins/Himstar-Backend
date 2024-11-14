from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import BannerOrVideo
from dashboard.models import Category
from .serializers import BannerOrVideoSerializer


class BannersByCategoryAPIView(APIView):
    def get(self, request, category_id=None):
        try:
            # If category_name is provided, filter by category
            if category_id:
                # Get the category object based on the name, with 404 handling
                category = get_object_or_404(Category, id=category_id)
                # Filter BannerOrVideo objects by category and media_type as 'banner'
                banners = BannerOrVideo.objects.filter(category=category, media_type=BannerOrVideo.BANNER)
            else:
                # If no category_name is provided, fetch all banners
                banners = BannerOrVideo.objects.filter(media_type=BannerOrVideo.BANNER)

            # Serialize the data
            serializer = BannerOrVideoSerializer(banners, many=True)

            # Return a JSON response with serialized data
            return Response({
                'banners': serializer.data
            }, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            # Generic exception handler for other unexpected errors
            return Response(
                {'error': 'An error occurred while retrieving banners.', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )