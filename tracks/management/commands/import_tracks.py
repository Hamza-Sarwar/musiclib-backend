"""
Management command to bulk import generated tracks from the generate_music.py script.

Usage:
    python manage.py import_tracks /path/to/generated_tracks/

This reads the metadata.json file and imports all tracks into Django.
"""
import json
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from tracks.models import Track, Genre, Mood


class Command(BaseCommand):
    help = "Import generated tracks from a directory with metadata.json"

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str, help="Path to generated_tracks directory")

    def handle(self, *args, **options):
        directory = options["directory"]
        meta_path = os.path.join(directory, "metadata.json")

        if not os.path.exists(meta_path):
            self.stderr.write(f"❌ metadata.json not found in {directory}")
            return

        with open(meta_path, "r") as f:
            tracks_data = json.load(f)

        imported = 0
        skipped = 0

        for track_data in tracks_data:
            # Check if track already exists
            if Track.objects.filter(title=track_data["title"]).exists():
                self.stdout.write(f"  ⏭ Skipped (exists): {track_data['title']}")
                skipped += 1
                continue

            # Get or create genre and mood
            genre = None
            mood = None
            if track_data.get("genre"):
                genre, _ = Genre.objects.get_or_create(
                    slug=track_data["genre"],
                    defaults={"name": track_data["genre"].replace("-", " ").title()},
                )
            if track_data.get("mood"):
                mood, _ = Mood.objects.get_or_create(
                    slug=track_data["mood"],
                    defaults={"name": track_data["mood"].title()},
                )

            # Get audio file
            filepath = os.path.join(directory, track_data["filename"])
            if not os.path.exists(filepath):
                # Try MP3 version
                mp3_path = filepath.replace(".wav", ".mp3")
                if os.path.exists(mp3_path):
                    filepath = mp3_path
                else:
                    self.stderr.write(f"  ❌ File not found: {filepath}")
                    continue

            # Create track
            track = Track(
                title=track_data["title"],
                description=f"AI-generated {track_data.get('genre', '')} track. {track_data.get('prompt', '')}",
                genre=genre,
                mood=mood,
                duration=track_data.get("duration", 0),
                bpm=track_data.get("bpm"),
                tags=f"{track_data.get('genre', '')}, {track_data.get('mood', '')}, ai generated, royalty free",
                is_active=True,
            )

            with open(filepath, "rb") as audio_file:
                ext = os.path.splitext(filepath)[1]
                track.audio_file.save(
                    f"{track_data['title'].lower().replace(' ', '_')}{ext}",
                    File(audio_file),
                    save=True,
                )

            imported += 1
            self.stdout.write(f"  ✅ Imported: {track_data['title']}")

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Import complete: {imported} imported, {skipped} skipped"
        ))
