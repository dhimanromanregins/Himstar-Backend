# serializers.py
from rest_framework import serializers
from .models import Category, Round, Tournament, Participant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'is_active']


# serializers.py
from rest_framework import serializers
from .models import Competition

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

class RoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Round
        fields = '__all__'

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['name', 'email', 'phone_number', 'video', 'competition']

class TournamentSerializer(serializers.ModelSerializer):
    rounds = RoundSerializer(many=True)

    class Meta:
        model = Tournament
        fields = ['name', 'description', 'rounds']