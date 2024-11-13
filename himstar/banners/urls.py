from django.urls import path
from .views import BannersByCategoryAPIView

urlpatterns = [
    path('api/banners/<str:category_name>/', BannersByCategoryAPIView.as_view(), name='banners_by_category_api'),
]
