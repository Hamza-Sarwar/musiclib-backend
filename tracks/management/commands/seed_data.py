from django.core.management.base import BaseCommand
from tracks.models import Genre, Mood


class Command(BaseCommand):
    help = "Seed database with initial genres and moods"

    def handle(self, *args, **options):
        genres = [
            ("Lo-Fi", "lofi"),
            ("Ambient", "ambient"),
            ("Corporate", "corporate"),
            ("Cinematic", "cinematic"),
            ("Acoustic", "acoustic"),
            ("Electronic", "electronic"),
            ("Jazz", "jazz"),
            ("Classical", "classical"),
            ("Hip Hop", "hip-hop"),
            ("Pop", "pop"),
            ("Rock", "rock"),
            ("R&B", "rnb"),
            ("World", "world"),
            ("Chillwave", "chillwave"),
        ]

        moods = [
            ("Calm", "calm"),
            ("Upbeat", "upbeat"),
            ("Energetic", "energetic"),
            ("Sad", "sad"),
            ("Happy", "happy"),
            ("Dramatic", "dramatic"),
            ("Mysterious", "mysterious"),
            ("Romantic", "romantic"),
            ("Relaxing", "relaxing"),
            ("Inspiring", "inspiring"),
            ("Dark", "dark"),
            ("Playful", "playful"),
            ("Epic", "epic"),
            ("Peaceful", "peaceful"),
        ]

        for name, slug in genres:
            Genre.objects.get_or_create(name=name, slug=slug)
            self.stdout.write(f"  ✓ Genre: {name}")

        for name, slug in moods:
            Mood.objects.get_or_create(name=name, slug=slug)
            self.stdout.write(f"  ✓ Mood: {name}")

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Seeded {len(genres)} genres and {len(moods)} moods"
        ))
