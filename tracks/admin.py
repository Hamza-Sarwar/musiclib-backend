from django.contrib import admin
from .models import Track, Genre, Mood


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = [
        "title", "genre", "mood", "duration_display",
        "bpm", "download_count", "is_active", "is_featured", "created_at",
    ]
    list_filter = ["genre", "mood", "is_active", "is_featured"]
    search_fields = ["title", "description", "tags"]
    list_editable = ["is_active", "is_featured"]
    readonly_fields = ["download_count", "play_count", "created_at", "updated_at"]
    
    fieldsets = (
        (None, {
            "fields": ("title", "description", "audio_file"),
        }),
        ("Categorization", {
            "fields": ("genre", "mood", "tags"),
        }),
        ("Audio Info", {
            "fields": ("duration", "bpm"),
        }),
        ("Status", {
            "fields": ("is_active", "is_featured"),
        }),
        ("Stats (read-only)", {
            "fields": ("download_count", "play_count", "created_at", "updated_at"),
        }),
    )
