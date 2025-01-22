# views.py
from rest_framework import generics
from .models import  Like, Comment, Favorite, Share,Participant
from .serializers import  LikeSerializer, CommentSerializer, FavoriteSerializer, ShareSerializer, ParticipantSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import platform
if platform.system() == 'Windows':
    from moviepy.editor import VideoFileClip, AudioFileClip
else:
    from moviepy import VideoFileClip, AudioFileClip
import requests
from datetime import date
import os
from django.core.files.storage import default_storage
import uuid
import threading
from django.shortcuts import get_object_or_404
from accounts.models import Register
from rest_framework.permissions import IsAuthenticated
from dashboard.models import Competition

today = date.today()
class ParticipantListCreateView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            register = Register.objects.filter(user=request.user).first()
            participant = Participant.objects.get(user=register)
        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParticipantSerializer(participant)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ParticipantSerializer(participant, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        competition_id = request.data['competition']
        register = Register.objects.filter(user=request.user).first()
        participant = Participant.objects.filter(competition=competition_id, user=register).first()
        if not participant:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)
        participant.video = participant.temp_video
        participant.temp_video = None
        participant.is_paid = True
        participant.save()
        return Response( status=status.HTTP_200_OK)

    def delete(self, request, pk):
        try:
            participant = Participant.objects.get(pk=pk)
        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=status.HTTP_404_NOT_FOUND)

        participant.delete()
        return Response({'detail': 'Participant deleted.'}, status=status.HTTP_204_NO_CONTENT)


# class PostShuffledListAPIView2(APIView):
#     def get(self, request, user):
#         # Filter posts by the specific user
#         posts = Post.objects.filter(user__id=user).order_by('?')  # or filter(user=user) if `user` is a ForeignKey
#         serializer = PostSerializer(posts, many=True, context={'user_id': user})
#         return Response(serializer.data, status=status.HTTP_200_OK)



class UserVideosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.GET.get('username')

        if username:
            user = Register.objects.filter(user__username=username).first()
        else:
            user = get_object_or_404(Register, user=request.user.id)

        # Fetch all Participant instances for the given user with non-empty video fields
        # participants = Participant.objects.filter(user=user).exclude(file_uri__isnull=True)
        participants = Participant.objects.filter(user=user, video__isnull=False).exclude(video="")
        print('participants>>>', participants)

        participants_serializer = ParticipantSerializer(participants, many=True, context={'user_id': request.user.id})

        return Response(participants_serializer.data, status=status.HTTP_200_OK)


class PostShuffledListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            value = request.query_params.get('value')
            split_value = value.split('-')
            if split_value[0] == "COMP":
                competition_id = int(split_value[1])
                participants_video = Participant.objects.filter(competition=competition_id,competition__start_date__lte=today,competition__end_date__gte=today).exclude(video__isnull=True).exclude(video__exact=''.order_by('?'))
            elif split_value[0] == "TOUR":
                tournament_id = split_value[1]
                participants_video = Participant.objects.filter(tournament=tournament_id,competition__start_date__lte=today,competition__end_date__gte=today).exclude(video__isnull=True).exclude(video__exact=''.order_by('?'))
            elif split_value[0] == "ALL":
                participants_video = Participant.objects.filter(
                    competition__isnull=False,
                    competition__start_date__lte=today,
                    competition__end_date__gte=today
                ).exclude(
                    video__isnull=True
                ).exclude(
                    video__exact=''
                ).order_by('?')



            else:
                return Response({'detail': 'query params not found'}, status=status.HTTP_404_NOT_FOUND)

            serializer = ParticipantSerializer(participants_video, many=True, context={'user_id': request.user.id})
            print(serializer.data, '---------------------------')
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as err:
            print('Error:', err)
            return Response({"detail": "An error occurred while fetching the participants."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LikeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user_id = request.user.id
        post_id = request.data.get('post_id')
        post = get_object_or_404(Participant, id=post_id)
        user_register = get_object_or_404(Register, user=user_id)
        like, created = Like.objects.get_or_create(user=user_register, post=post)
        if not created:
            like.delete()
            user_register.votes = max(user_register.votes - 1, 0) 
            user_register.save()
            return Response({"message": "Post unliked"}, status=status.HTTP_200_OK)
        user_register.votes += 1
        user_register.save()
        return Response({"message": "Post liked"}, status=status.HTTP_200_OK)



class CommentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        register = Register.objects.filter(user=request.user).first()
        request.data['user'] = register.id
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class LikeListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, post_id):
        if not post_id:
            return Response({'error': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        likes = Like.objects.filter(post__id=post_id)
        serializer = LikeSerializer(likes, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, post_id):
        if not post_id:
            return Response({'error': 'Post not found!'}, status=status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post__id=post_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FavoriteListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FavoriteDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ShareListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ShareDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Share.objects.all()
    serializer_class = ShareSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MergeVideoAndMusic(APIView):
    @staticmethod
    def cleanup_files(video_path, music_path):
        """Asynchronous cleanup of temporary files."""
        try:
            video_path = os.path.join('media', video_path)
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(music_path):
                os.remove(music_path)
        except Exception as e:
            print(f"Failed to delete temporary files: {str(e)}")

    def post(self, request):
        print('request.data>>>', request.data)
        video_file = request.FILES.get('video')
        music_url = request.data.get('music')
        competition_id = request.data.get('competition_id')
        print('competition_id>>>', competition_id);

        if not video_file or not music_url or not competition_id:
            return Response({"error": "Video file, music URL, and competition ID are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        register = Register.objects.filter(user=request.user).first()
        competition = Competition.objects.filter(id=competition_id).first()
        if not register or not competition:
            return Response({"error": "User or competition not found."},
                            status=status.HTTP_404_NOT_FOUND)

        # os.makedirs('media', exist_ok=True)
        # os.makedirs('media/temp_videos', exist_ok=True)
        temp_video_dir = os.path.join('media', 'temp_videos')
        os.makedirs(temp_video_dir, exist_ok=True)
        video_file_extension = video_file.name.split('.')[-1]
        video_filename = f"{uuid.uuid4().hex}.{video_file_extension}"
        video_path = default_storage.save(os.path.join('temp_videos', video_filename), video_file)
       
        video_path = os.path.join('media', video_path)
         # Download the music file from the URL
        music_path = os.path.join('media', f"{uuid.uuid4().hex}.mp3")
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
            video_clip = VideoFileClip(video_path)
            if video_clip.duration > 60:
                return Response({"error": "Video duration must be less than or equal to 60 seconds"},
                                status=status.HTTP_400_BAD_REQUEST)
            audio_clip = AudioFileClip(music_path)
            min_duration = min(video_clip.duration, audio_clip.duration)
            if platform.system() == 'Windows':
                video_clip = video_clip.subclip(0, min_duration)
                audio_clip = audio_clip.subclip(0, min_duration)
                final_clip = video_clip.set_audio(audio_clip)
            else:
                video_clip = video_clip.subclipped(0, min_duration)
                audio_clip = audio_clip.subclipped(0, min_duration)
                final_clip = video_clip.with_audio(audio_clip)

            # Save the merged video
            merged_video_name = f"{uuid.uuid4().hex}.mp4"
            output_path = os.path.join('media', "merged_videos", merged_video_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            final_clip.write_videofile(output_path, codec="libx264", preset='slow',bitrate='1500k', threads=4, ffmpeg_params=["-vf", "setsar=1"])

            participant, _ = Participant.objects.get_or_create(user=register, competition=competition)
            participant.temp_video = f"merged_videos/{merged_video_name}"
            participant.save()
        except Exception as e:
            print(e, '---------')
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
        return Response({"merged_video": f"media/merged_videos/{merged_video_name}"},
                        status=status.HTTP_200_OK)


class RemoveTempVideo(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        competition_id = request.data.get('competition_id')
        if not competition_id:
            return Response({"error": "Competition not found!"},
                            status=status.HTTP_404_NOT_FOUND)
        register = Register.objects.filter(user=request.user).first()
        participant = Participant.objects.filter(competition=competition_id, user=register).first()
        if not participant:
            return Response({"error": "Participant not found!"},
                        status=status.HTTP_404_NOT_FOUND)
        participant.delete()
        return Response(status=status.HTTP_200_OK)
class ParticipantTempSave(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        competition_id = request.data.get('competition')
        video = request.FILES.get('video')
        if not video or not competition_id:
            return Response({"error": "Video file and competition ID are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        register = Register.objects.filter(user=request.user).first()
        competition = Competition.objects.filter(id=competition_id).first()
        if not competition:
            return Response({'detail': 'Competition not found.'}, status=status.HTTP_404_NOT_FOUND)

        participant, _ = Participant.objects.get_or_create(competition=competition, user=register)

        participant.temp_video = video
        participant.save()
        return Response(status=status.HTTP_200_OK)
