import mimetypes
import os
import re

from django.db.models import F
from django.http import FileResponse, StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Track, Genre, Mood
from .serializers import (
    TrackListSerializer,
    TrackDetailSerializer,
    GenreSerializer,
    MoodSerializer,
)
from .filters import TrackFilter


def _get_audio_content_type(filename):
    """Determine content type from file extension."""
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


class TrackViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for browsing and downloading tracks.

    list: GET /api/tracks/
    retrieve: GET /api/tracks/{id}/
    stream: GET /api/tracks/{id}/stream/ (supports Range requests for mobile)
    download: GET /api/tracks/{id}/download/
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
    def stream(self, request, pk=None):
        """
        Stream a track with HTTP Range request support.

        This is the endpoint mobile browsers need — they send Range headers
        and expect 206 Partial Content responses to play audio.
        """
        track = self.get_object()

        try:
            audio_file = track.audio_file
            file_size = audio_file.size
            content_type = _get_audio_content_type(audio_file.name)
        except (FileNotFoundError, ValueError):
            return Response(
                {"error": "File not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        range_header = request.META.get("HTTP_RANGE", "")
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)

        if range_match:
            # Partial content (206) — required by mobile browsers
            start = int(range_match.group(1))
            end = int(range_match.group(2)) if range_match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1

            f = audio_file.open("rb")
            f.seek(start)
            data = f.read(length)
            f.close()

            response = StreamingHttpResponse(
                iter([data]),
                status=206,
                content_type=content_type,
            )
            response["Content-Length"] = length
            response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        else:
            # Full file (200)
            response = FileResponse(
                audio_file.open("rb"),
                content_type=content_type,
            )
            response["Content-Length"] = file_size

        response["Accept-Ranges"] = "bytes"
        response["Content-Disposition"] = "inline"
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Headers"] = "Range"
        response["Access-Control-Expose-Headers"] = "Content-Range, Content-Length, Accept-Ranges"
        response["Cache-Control"] = "public, max-age=86400"
        return response

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download a track and increment the download counter."""
        track = self.get_object()

        # Increment download count atomically
        Track.objects.filter(pk=track.pk).update(download_count=F("download_count") + 1)

        try:
            content_type = _get_audio_content_type(track.audio_file.name)
            response = FileResponse(
                track.audio_file.open("rb"),
                content_type=content_type,
            )
            # Use original file extension instead of hardcoding .mp3
            ext = os.path.splitext(track.audio_file.name)[1] or ".mp3"
            filename = f"{track.title.replace(' ', '_')}{ext}"
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
