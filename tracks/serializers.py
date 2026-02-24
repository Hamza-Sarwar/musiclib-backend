from rest_framework import serializers
from .models import Track, Genre, Mood


class GenreSerializer(serializers.ModelSerializer):
    track_count = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "track_count"]

    def get_track_count(self, obj):
        return obj.tracks.filter(is_active=True).count()


class MoodSerializer(serializers.ModelSerializer):
    track_count = serializers.SerializerMethodField()

    class Meta:
        model = Mood
        fields = ["id", "name", "slug", "track_count"]

    def get_track_count(self, obj):
        return obj.tracks.filter(is_active=True).count()


class TrackListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    genre_name = serializers.CharField(source="genre.name", read_only=True, default=None)
    mood_name = serializers.CharField(source="mood.name", read_only=True, default=None)
    duration_display = serializers.ReadOnlyField()
    file_size = serializers.ReadOnlyField()
    audio_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            "id", "title", "genre_name", "mood_name",
            "duration", "duration_display", "bpm",
            "download_count", "play_count",
            "audio_url", "download_url", "file_size",
            "is_featured", "created_at",
        ]

    def get_audio_url(self, obj):
        """Returns the streaming URL (supports Range requests for mobile)."""
        request = self.context.get("request")
        if obj.audio_file and request:
            from django.urls import reverse
            stream_path = reverse("track-stream", kwargs={"pk": obj.pk})
            return request.build_absolute_uri(stream_path)
        return None

    def get_download_url(self, obj):
        """Returns the download URL."""
        request = self.context.get("request")
        if obj.audio_file and request:
            from django.urls import reverse
            download_path = reverse("track-download", kwargs={"pk": obj.pk})
            return request.build_absolute_uri(download_path)
        return None


class TrackDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail views."""
    genre = GenreSerializer(read_only=True)
    mood = MoodSerializer(read_only=True)
    duration_display = serializers.ReadOnlyField()
    file_size = serializers.ReadOnlyField()
    audio_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            "id", "title", "description",
            "genre", "mood", "tags_list",
            "duration", "duration_display", "bpm",
            "download_count", "play_count",
            "audio_url", "download_url", "file_size",
            "waveform_data",
            "is_featured", "created_at",
        ]

    def get_audio_url(self, obj):
        """Returns the streaming URL (supports Range requests for mobile)."""
        request = self.context.get("request")
        if obj.audio_file and request:
            from django.urls import reverse
            stream_path = reverse("track-stream", kwargs={"pk": obj.pk})
            return request.build_absolute_uri(stream_path)
        return None

    def get_download_url(self, obj):
        """Returns the download URL."""
        request = self.context.get("request")
        if obj.audio_file and request:
            from django.urls import reverse
            download_path = reverse("track-download", kwargs={"pk": obj.pk})
            return request.build_absolute_uri(download_path)
        return None

    def get_tags_list(self, obj):
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(",") if tag.strip()]
        return []
