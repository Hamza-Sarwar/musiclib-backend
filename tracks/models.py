import uuid
from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Mood(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Categorization
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, related_name="tracks")
    mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, related_name="tracks")
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")

    # Artist & Language
    artist_name = models.CharField(max_length=100, blank=True, help_text="AI artist persona name")
    language = models.CharField(max_length=20, blank=True, default="English", help_text="Track language")

    # Lyrics (optional)
    lyrics = models.TextField(blank=True, help_text="Song lyrics or spoken word text")

    # Audio file
    audio_file = models.FileField(upload_to="tracks/%Y/%m/", blank=True)
    
    # Metadata
    duration = models.PositiveIntegerField(help_text="Duration in seconds", default=0)
    bpm = models.PositiveIntegerField(null=True, blank=True, help_text="Beats per minute")
    
    # Waveform image (optional, for frontend visualization)
    waveform_data = models.JSONField(null=True, blank=True, help_text="Waveform peaks data")
    
    # Stats
    download_count = models.PositiveIntegerField(default=0)
    play_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-download_count"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["genre", "mood"]),
        ]

    def __str__(self):
        return self.title

    @property
    def duration_display(self):
        """Return duration as MM:SS format."""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def file_size(self):
        """Return file size in MB."""
        try:
            return round(self.audio_file.size / (1024 * 1024), 1)
        except (FileNotFoundError, ValueError):
            return 0
