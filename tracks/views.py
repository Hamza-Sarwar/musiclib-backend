import os

from django.conf import settings
from django.db.models import F, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.http import FileResponse

from .models import Track, Genre, Mood
from .serializers import (
    TrackListSerializer,
    TrackDetailSerializer,
    GenreSerializer,
    MoodSerializer,
)
from .filters import TrackFilter


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for browsing and downloading tracks.

    list: GET /api/tracks/
    retrieve: GET /api/tracks/{id}/
    download: GET /api/tracks/{id}/download/
    play: POST /api/tracks/{id}/play/
    similar: GET /api/tracks/{id}/similar/
    genres: GET /api/tracks/genres/
    moods: GET /api/tracks/moods/
    featured: GET /api/tracks/featured/
    popular: GET /api/tracks/popular/
    """
    queryset = Track.objects.filter(is_active=True).select_related("genre", "mood")
    filterset_class = TrackFilter
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "download_count", "play_count", "duration", "bpm"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TrackDetailSerializer
        return TrackListSerializer

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download a track and increment the download counter."""
        track = self.get_object()

        if not track.audio_file:
            return Response(
                {"error": "No audio file available"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            file = track.audio_file.open("rb")
        except FileNotFoundError:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Increment download count atomically
        Track.objects.filter(pk=track.pk).update(download_count=F("download_count") + 1)

        # Detect content type from extension
        ext = os.path.splitext(track.audio_file.name)[1].lower()
        content_types = {".wav": "audio/wav", ".mp3": "audio/mpeg", ".flac": "audio/flac"}
        content_type = content_types.get(ext, "application/octet-stream")

        response = FileResponse(file, content_type=content_type)
        clean_title = track.title.replace(' ', '_')
        filename = f"{clean_title}{ext or '.wav'}"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(detail=True, methods=["post"])
    def play(self, request, pk=None):
        """Increment play count (called when user plays a track)."""
        track = self.get_object()
        Track.objects.filter(pk=track.pk).update(play_count=F("play_count") + 1)
        return Response({"status": "ok"})

    @action(detail=True, methods=["get"])
    def similar(self, request, pk=None):
        """Return tracks with the same genre or mood, excluding self."""
        track = self.get_object()
        filters = Q()
        if track.genre:
            filters |= Q(genre=track.genre)
        if track.mood:
            filters |= Q(mood=track.mood)

        similar = (
            self.queryset.filter(filters)
            .exclude(pk=track.pk)
            .order_by("-download_count")[:10]
        )
        serializer = TrackListSerializer(
            similar, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def genres(self, request):
        """List all genres with track counts."""
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def moods(self, request):
        """List all moods with track counts."""
        moods = Mood.objects.all()
        serializer = MoodSerializer(moods, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def languages(self, request):
        """List distinct languages."""
        langs = (
            self.queryset.exclude(language="")
            .values_list("language", flat=True)
            .distinct()
            .order_by("language")
        )
        return Response(list(langs))

    @action(detail=False, methods=["get"])
    def artists(self, request):
        """List distinct artist names."""
        artists = (
            self.queryset.exclude(artist_name="")
            .values_list("artist_name", flat=True)
            .distinct()
            .order_by("artist_name")
        )
        return Response(list(artists))

    @action(detail=False, methods=["get"])
    def featured(self, request):
        """List featured tracks."""
        tracks = self.queryset.filter(is_featured=True)[:10]
        serializer = TrackListSerializer(tracks, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def popular(self, request):
        """List most downloaded tracks."""
        tracks = self.queryset.order_by("-download_count")[:20]
        serializer = TrackListSerializer(tracks, many=True, context={"request": request})
        return Response(serializer.data)


@api_view(["POST"])
def upload_audio(request):
    """Upload audio file for a track (protected by UPLOAD_SECRET)."""
    secret = request.headers.get("X-Upload-Secret", "")
    expected = os.environ.get("UPLOAD_SECRET", "")
    if not expected or secret != expected:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    title = request.data.get("title")
    audio = request.FILES.get("audio")
    if not title or not audio:
        return Response({"error": "title and audio required"}, status=status.HTTP_400_BAD_REQUEST)

    # Find or create track
    track = Track.objects.filter(title=title).first()
    if not track:
        genre_slug = request.data.get("genre", "")
        mood_slug = request.data.get("mood", "")
        genre = Genre.objects.filter(slug=genre_slug).first()
        mood = Mood.objects.filter(slug=mood_slug).first()
        track = Track.objects.create(
            title=title,
            artist_name=request.data.get("artist_name", ""),
            language=request.data.get("language", "English"),
            genre=genre,
            mood=mood,
            bpm=int(request.data.get("bpm", 0)) or None,
            duration=int(request.data.get("duration", 28)),
            lyrics=request.data.get("lyrics", ""),
            description=request.data.get("description", ""),
            tags=f"{genre_slug}, {mood_slug}",
            is_active=True,
        )

    track.audio_file = audio
    track.save()
    return Response({"status": "ok", "id": str(track.id), "title": track.title})
