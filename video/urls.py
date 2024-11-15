# urls.py
from django.urls import path
from .views import (
    PostCreateAPIView, PostDetailView,
    LikeAPIView, LikeDetailView,
    CommentCreateAPIView, CommentDetailView,
    FavoriteListCreateView, FavoriteDetailView,
    ShareListCreateView, ShareDetailView,
    MergeVideoAndMusic, RemoveMergedVideo,
    PostShuffledListAPIView, LikeListView,PostShuffledListAPIView2
)

urlpatterns = [
    path('posts/', PostCreateAPIView.as_view(), name='post-list-create'),
    path('list-posts/<int:user>/', PostShuffledListAPIView.as_view(), name='post-list-view'),
    path('user-posts/<int:user>/', PostShuffledListAPIView2.as_view(), name='user-post-list-view'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path('like-post/', LikeAPIView.as_view(), name='like-create'),
    path('list-likes/<int:post_id>/', LikeListView.as_view(), name='like-list-view'),
    path('likes/<int:pk>/', LikeDetailView.as_view(), name='like-detail'),

    path('comment-post/', CommentCreateAPIView.as_view(), name='comment-create'),
    path('list-comments/<int:post_id>/', CommentDetailView.as_view(), name='comment-detail'),

    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/<int:pk>/', FavoriteDetailView.as_view(), name='favorite-detail'),

    path('shares/', ShareListCreateView.as_view(), name='share-list-create'),
    path('shares/<int:pk>/', ShareDetailView.as_view(), name='share-detail'),

    path('merge-video/', MergeVideoAndMusic.as_view(), name='merge_video_and_music'),
    path('remove-merged-video/', RemoveMergedVideo.as_view(), name='remove_merged_video'),
]
