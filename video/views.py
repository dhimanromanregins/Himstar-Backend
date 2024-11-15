# views.py
from rest_framework import generics
from .models import Post, Like, Comment, Favorite, Share
from .serializers import PostSerializer, LikeSerializer, CommentSerializer, FavoriteSerializer, ShareSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from moviepy.editor import VideoFileClip, AudioFileClip
import requests
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import uuid
import threading
import time
from django.shortcuts import get_object_or_404
from accounts.models import Register


class PostCreateAPIView(APIView):
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostShuffledListAPIView2(APIView):
    def get(self, request, user):
        # Filter posts by the specific user
        posts = Post.objects.filter(user__id=user).order_by('?')  # or filter(user=user) if `user` is a ForeignKey
        serializer = PostSerializer(posts, many=True, context={'user_id': user})
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostShuffledListAPIView(APIView):
    def get(self, request, user):
        posts = Post.objects.all().order_by('?')
        serializer = PostSerializer(posts, many=True, context={'user_id': user})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LikeAPIView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')
        post = get_object_or_404(Post, id=post_id)

        user = Register.objects.filter(id=user_id).first()

        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
            return Response({"message": "Post unliked"}, status=status.HTTP_200_OK)

        return Response({"message": "Post liked"}, status=status.HTTP_200_OK)


class CommentCreateAPIView(APIView):
    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeDetailView(generics.RetrieveDestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LikeListView(APIView):
    def get(self, request, post_id):
        if not post_id:
            return Response({'error': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        likes = Like.objects.filter(post__id=post_id)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentListCreateView(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    def get(self, request, post_id):
        if not post_id:
            return Response({'error': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post__id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteListCreateView(generics.ListCreateAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FavoriteDetailView(generics.RetrieveDestroyAPIView):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ShareListCreateView(generics.ListCreateAPIView):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ShareDetailView(generics.RetrieveDestroyAPIView):
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MergeVideoAndMusic(APIView):
    @staticmethod
    def cleanup_files(video_path, music_path):
        """Asynchronous cleanup of temporary files."""
        try:
            video_path = os.path.join(settings.MEDIA_ROOT, video_path)
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(music_path):
                os.remove(music_path)
        except Exception as e:
            print(f"Failed to delete temporary files: {str(e)}")

    def post(self, request):
        video_file = request.FILES.get('video')
        music_url = request.data.get('music')

        if not video_file or not music_url:
            return Response({"error": "Video file and music URL are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save video file temporarily
        video_path = default_storage.save(f"temp_videos/{video_file.name}", video_file)

        # Download the music file from the URL
        music_path = os.path.join(settings.MEDIA_ROOT, f"{uuid.uuid4().hex}.mp3")
        try:
            with requests.get(music_url, stream=True) as r:
                r.raise_for_status()
                with open(music_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.RequestException:
            return Response({"error": "Something went wrong, please try again!"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Merge video and music
        video_clip = None
        audio_clip = None
        try:
            video_clip = VideoFileClip('media/' + video_path)
            if video_clip.duration > 60:
                return Response({"error": "Video duration must be less than or equal to 60 seconds"},
                                status=status.HTTP_400_BAD_REQUEST)
            audio_clip = AudioFileClip(music_path)
            min_duration = min(video_clip.duration, audio_clip.duration)
            video_clip = video_clip.subclip(0, min_duration)
            audio_clip = audio_clip.subclip(0, min_duration)
            final_clip = video_clip.set_audio(audio_clip)

            # Save the merged video
            merged_video_name = f"{uuid.uuid4().hex}.mp4"
            output_path = os.path.join(settings.MEDIA_ROOT, "merged_videos", merged_video_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            final_clip.write_videofile(output_path, codec="libx264")
        except Exception as e:
            return Response({"error": f"Something went wrong, please try again!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            # Clean up temporary files
            if video_clip:
                video_clip.close()
            if audio_clip:
                audio_clip.close()
            cleanup_thread = threading.Thread(target=self.cleanup_files, args=(video_path, music_path))
            cleanup_thread.start()

        # Return the path to the merged video
        return Response({"merged_video": f"{settings.MEDIA_URL}merged_videos/{merged_video_name}"},
                        status=status.HTTP_200_OK)


class RemoveMergedVideo(APIView):
    def post(self, request):
        file = request.data.get('file')
        if not file:
            return Response({"error": "File not found!"},
                            status=status.HTTP_404_NOT_FOUND)

        try:
            file_path = os.path.join(settings.MEDIA_ROOT, "merged_videos", file)
            if os.path.exists(file_path):
                os.remove(file_path)
                return Response({"message": "File deleted successfully."},
                                status=status.HTTP_200_OK)
            else:
                return Response({"error": "File does not exist."},
                                status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Something went wrong, please try again!"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
