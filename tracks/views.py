from django.db.models import F, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
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

        # Increment download count atomically
        Track.objects.filter(pk=track.pk).update(download_count=F("download_count") + 1)

        try:
            response = FileResponse(
                track.audio_file.open("rb"),
                content_type="audio/mpeg",
            )
            # Clean filename
            filename = f"{track.title.replace(' ', '_')}.mp3"
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except FileNotFoundError:
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

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
