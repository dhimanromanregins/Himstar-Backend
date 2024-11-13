# urls.py
from django.urls import path
from .views import (
    PostListCreateView, PostDetailView,
    LikeListCreateView, LikeDetailView,
    CommentListCreateView, CommentDetailView,
    FavoriteListCreateView, FavoriteDetailView,
    ShareListCreateView, ShareDetailView
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path('likes/', LikeListCreateView.as_view(), name='like-list-create'),
    path('likes/<int:pk>/', LikeDetailView.as_view(), name='like-detail'),

    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),

    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/<int:pk>/', FavoriteDetailView.as_view(), name='favorite-detail'),

    path('shares/', ShareListCreateView.as_view(), name='share-list-create'),
    path('shares/<int:pk>/', ShareDetailView.as_view(), name='share-detail'),
]
