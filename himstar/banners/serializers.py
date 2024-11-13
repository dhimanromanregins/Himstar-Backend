from rest_framework import serializers
from .models import BannerOrVideo

class BannerOrVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerOrVideo
        fields = ['title', 'description', 'banner_image']
