# serializers.py
from rest_framework import serializers
from .models import Category, Round, Tournament, Participant

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


# serializers.py
from rest_framework import serializers
from .models import Competition

class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['category'] = instance.category.name
        return representation

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