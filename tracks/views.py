import io
import math
import mimetypes
import os
import random
import re
import struct
import wave

from django.conf import settings
from django.core.files.base import ContentFile
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


def _generate_wav(duration_sec=10, sample_rate=22050, freq=440.0):
    """Generate a simple sine-wave WAV file in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(sample_rate * duration_sec):
            sample = int(16000 * math.sin(2 * math.pi * freq * i / sample_rate))
            wf.writeframes(struct.pack("<h", sample))
    buf.seek(0)
    return buf.read()


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

    @action(detail=False, methods=["post"])
    def seed(self, request):
        """Create sample tracks. Protected by SEED_API_KEY."""
        seed_key = os.getenv("SEED_API_KEY", "")
        provided_key = request.headers.get("X-Seed-Key", "")
        if not seed_key or provided_key != seed_key:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        count = min(int(request.data.get("count", 5)), 20)

        SAMPLE_TRACKS = [
            {"title": "Midnight Drive", "genre": "Lo-Fi", "mood": "Chill", "tags": "lofi,chill,night,drive", "bpm": 85, "duration": 12, "freq": 330},
            {"title": "Neon Pulse", "genre": "Electronic", "mood": "Energetic", "tags": "electronic,synth,upbeat", "bpm": 128, "duration": 10, "freq": 440},
            {"title": "Autumn Leaves", "genre": "Acoustic", "mood": "Calm", "tags": "acoustic,guitar,peaceful", "bpm": 72, "duration": 14, "freq": 294},
            {"title": "Urban Groove", "genre": "Hip Hop", "mood": "Energetic", "tags": "hiphop,beat,urban,groove", "bpm": 95, "duration": 11, "freq": 370},
            {"title": "Starlight Serenade", "genre": "Ambient", "mood": "Dreamy", "tags": "ambient,space,dreamy", "bpm": 60, "duration": 15, "freq": 262},
            {"title": "Electric Sunset", "genre": "Electronic", "mood": "Chill", "tags": "electronic,sunset,mellow", "bpm": 110, "duration": 10, "freq": 392},
            {"title": "Morning Coffee", "genre": "Jazz", "mood": "Calm", "tags": "jazz,morning,smooth", "bpm": 80, "duration": 13, "freq": 350},
            {"title": "Thunder Road", "genre": "Rock", "mood": "Energetic", "tags": "rock,guitar,powerful", "bpm": 140, "duration": 10, "freq": 494},
            {"title": "Ocean Whisper", "genre": "Ambient", "mood": "Calm", "tags": "ambient,ocean,waves,relax", "bpm": 55, "duration": 16, "freq": 247},
            {"title": "City Lights", "genre": "Lo-Fi", "mood": "Dreamy", "tags": "lofi,city,night,chill", "bpm": 78, "duration": 12, "freq": 311},
            {"title": "Solar Flare", "genre": "Electronic", "mood": "Energetic", "tags": "electronic,intense,dance", "bpm": 135, "duration": 10, "freq": 523},
            {"title": "Rainy Window", "genre": "Acoustic", "mood": "Melancholy", "tags": "acoustic,rain,sad,piano", "bpm": 65, "duration": 14, "freq": 277},
            {"title": "Bass Drop", "genre": "Hip Hop", "mood": "Energetic", "tags": "hiphop,bass,heavy,beat", "bpm": 100, "duration": 10, "freq": 220},
            {"title": "Velvet Moon", "genre": "Jazz", "mood": "Dreamy", "tags": "jazz,night,smooth,sax", "bpm": 70, "duration": 13, "freq": 330},
            {"title": "Crystal Cave", "genre": "Ambient", "mood": "Calm", "tags": "ambient,crystal,ethereal", "bpm": 50, "duration": 15, "freq": 523},
        ]

        random.shuffle(SAMPLE_TRACKS)
        created = []

        for item in SAMPLE_TRACKS[:count]:
            genre, _ = Genre.objects.get_or_create(
                name=item["genre"],
                defaults={"slug": item["genre"].lower().replace(" ", "-")},
            )
            mood, _ = Mood.objects.get_or_create(
                name=item["mood"],
                defaults={"slug": item["mood"].lower().replace(" ", "-")},
            )

            wav_data = _generate_wav(
                duration_sec=item["duration"],
                freq=item["freq"],
            )

            track = Track(
                title=item["title"],
                genre=genre,
                mood=mood,
                tags=item["tags"],
                bpm=item["bpm"],
                duration=item["duration"],
            )
            track.audio_file.save(
                f"{item['title'].lower().replace(' ', '_')}.wav",
                ContentFile(wav_data),
                save=False,
            )
            track.save()
            created.append(track.title)

        return Response({"created": created, "count": len(created)})
