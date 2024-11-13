# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from .models import Category
from django.shortcuts import get_object_or_404
from .models import Competition, Category, Round, Tournament, Participant, CompetitionMedia
from .serializers import CategorySerializer,CompetitionSerializer, RoundSerializer, TournamentSerializer, ParticipantSerializer

class CompetitionListCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        competitions = Competition.objects.all()
        serializer = CompetitionSerializer(competitions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CompetitionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List all categories
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# Retrieve a single category by ID
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CompetitionDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            competition = Competition.objects.get(pk=pk)
        except Competition.DoesNotExist:
            return Response({'detail': 'Competition not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompetitionSerializer(competition)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            competition = Competition.objects.get(pk=pk)
        except Competition.DoesNotExist:
            return Response({'detail': 'Competition not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = CompetitionSerializer(competition, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            competition = Competition.objects.get(pk=pk)
        except Competition.DoesNotExist:
            return Response({'detail': 'Competition not found.'}, status=status.HTTP_404_NOT_FOUND)

        competition.delete()
        return Response({'detail': 'Competition deleted.'}, status=status.HTTP_204_NO_CONTENT)


# API View for Round
class RoundListCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        rounds = Round.objects.all()
        serializer = RoundSerializer(rounds, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoundDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            round_instance = Round.objects.get(pk=pk)
        except Round.DoesNotExist:
            return Response({'detail': 'Round not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoundSerializer(round_instance)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            round_instance = Round.objects.get(pk=pk)
        except Round.DoesNotExist:
            return Response({'detail': 'Round not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = RoundSerializer(round_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            round_instance = Round.objects.get(pk=pk)
        except Round.DoesNotExist:
            return Response({'detail': 'Round not found.'}, status=status.HTTP_404_NOT_FOUND)

        round_instance.delete()
        return Response({'detail': 'Round deleted.'}, status=status.HTTP_204_NO_CONTENT)


# API View for Participant
class ParticipantListCreateView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        participants = Participant.objects.all()
        serializer = ParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    def post(self, request, competition_pk):
        competition = Competition.objects.get(pk=competition_pk)
        serializer = ParticipantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(competition=competition)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParticipantDetailView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParticipantSerializer(participant)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParticipantSerializer(participant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        participant.delete()
        return Response({'detail': 'Participant deleted.'}, status=status.HTTP_204_NO_CONTENT)


# Custom API to eliminate participants (Elimination logic for rounds)
class EliminateParticipantsView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, round_id):
        try:
            round_instance = Round.objects.get(pk=round_id)
        except Round.DoesNotExist:
            return Response({'detail': 'Round not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Eliminate participants (custom logic, for example, eliminating 20%)
        participants = round_instance.participants.all()
        eliminated_count = int(len(participants) * 0.20)
        eliminated_participants = participants[:eliminated_count]

        for participant in eliminated_participants:
            participant.is_active = False
            participant.save()

        return Response({'detail': f'{eliminated_count} participants have been eliminated.'}, status=status.HTTP_200_OK)


# Custom API to start the next round of a tournament
class StartNextRoundView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, tournament_id):
        try:
            tournament = Tournament.objects.get(pk=tournament_id)
        except Tournament.DoesNotExist:
            return Response({'detail': 'Tournament not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the tournament has more rounds and start the next round
        if tournament.current_round < tournament.total_rounds:
            tournament.current_round += 1
            tournament.save()
            return Response({'detail': f'Round {tournament.current_round} has started.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'No more rounds left in the tournament.'}, status=status.HTTP_400_BAD_REQUEST)


class CompetitionsByCategoryView(APIView):
    def get(self, request, category_name):
        category = get_object_or_404(Category, name=category_name)
        competitions = Competition.objects.filter(category=category, is_active=True)
        serializer = CompetitionSerializer(competitions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)