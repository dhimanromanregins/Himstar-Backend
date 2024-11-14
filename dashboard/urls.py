# urls.py
from django.urls import path
from .views import CompetitionsByCategoryView, CategoryListView,CategoryDetailView , CompetitionListCreateView, CompetitionDetailView, RoundListCreateView, RoundDetailView, ParticipantListCreateView, ParticipantDetailView, EliminateParticipantsView, StartNextRoundView

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('api/competitions/<str:category_id>/', CompetitionsByCategoryView.as_view(), name='competitions_by_category'),
    path('api/competitions/', CompetitionListCreateView.as_view(), name='competition-list-create'),
    path('api/competitions/<int:pk>/', CompetitionDetailView.as_view(), name='competition-detail'),
    path('api/rounds/', RoundListCreateView.as_view(), name='round-list-create'),
    path('api/rounds/<int:pk>/', RoundDetailView.as_view(), name='round-detail'),
    path('api/participants/<int:competition_pk>/', ParticipantListCreateView.as_view(), name='round-participants')
]
