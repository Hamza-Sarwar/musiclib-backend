"""Seed the database with sample track metadata (no audio files needed)."""
from django.core.management.base import BaseCommand
from tracks.models import Track, Genre, Mood


SAMPLE_TRACKS = [
    {"title": "Paper Moon", "artist_name": "Aria Vale", "language": "English", "genre": "pop", "mood": "romantic", "bpm": 90, "duration": 28,
     "lyrics": "Hanging wishes on a paper moon\nHoping that you'd find me soon\nSoft guitar beneath the silver light\nDreaming of you every night\n\nFold me into constellations\nWhispered words and sweet sensations\nPaper moon above the sea\nShining down on you and me"},
    {"title": "Glass Houses", "artist_name": "Aria Vale", "language": "English", "genre": "pop", "mood": "sad", "bpm": 78, "duration": 28,
     "lyrics": "We built our love in glass houses\nEvery crack let the cold wind in\nFragile walls and silent promises\nShattered by the noise within"},
    {"title": "Morning Gold", "artist_name": "Aria Vale", "language": "English", "genre": "acoustic", "mood": "peaceful", "bpm": 88, "duration": 28,
     "lyrics": "Morning gold pours through the curtain\nCoffee steam and birdsong certain\nBarefoot steps on wooden floors\nPeaceful mornings, nothing more"},
    {"title": "Concrete Shadows", "artist_name": "Shadow", "language": "English", "genre": "hip-hop", "mood": "dark", "bpm": 140, "duration": 28,
     "lyrics": "Moving through concrete shadows at night\nCity breathing under neon light\n808 bass shaking the ground below\nEvery step part of the show"},
    {"title": "Binary Code", "artist_name": "Shadow", "language": "English", "genre": "electronic", "mood": "mysterious", "bpm": 128, "duration": 28,
     "lyrics": "Written in binary code\nZeros and ones down this road\nDigital glitches in my mind\nLeaving the real world behind"},
    {"title": "Stardust Lullaby", "artist_name": "Luna Ray", "language": "English", "genre": "ambient", "mood": "peaceful", "bpm": 55, "duration": 28,
     "lyrics": "Close your eyes and drift away\nStardust falling where you lay\nCrystal pads like gentle rain\nWashing over every pain"},
    {"title": "Electric Horizon", "artist_name": "Kai Storm", "language": "English", "genre": "rock", "mood": "energetic", "bpm": 135, "duration": 28,
     "lyrics": "Chasing the electric horizon\nGuitar riffs like bolts of lightning\nDrums pounding in my chest\nNever stopping, never rest"},
    {"title": "Quantum Leap", "artist_name": "Nova", "language": "English", "genre": "electronic", "mood": "energetic", "bpm": 128, "duration": 28,
     "lyrics": "Take the quantum leap tonight\nSynth waves crashing, neon light\nDriving beats beneath our feet\nFuture rhythms, feel the heat"},
    {"title": "Smoky Blues", "artist_name": "Ella Rivers", "language": "English", "genre": "jazz", "mood": "calm", "bpm": 85, "duration": 28,
     "lyrics": "Smoky blues in a dim-lit room\nSaxophone cutting through the gloom\nBrushed drums whisper on the snare\nJazz notes floating through the air"},
    {"title": "Autumn Waltz", "artist_name": "Victor Crane", "language": "English", "genre": "classical", "mood": "sad", "bpm": 72, "duration": 28,
     "lyrics": "Autumn leaves waltz to the ground\nPiano notes the only sound\nMelancholic melody plays\nFor all the golden fading days"},
    {"title": "Rise Again", "artist_name": "Victor Crane", "language": "English", "genre": "cinematic", "mood": "epic", "bpm": 130, "duration": 28,
     "lyrics": "When the world has knocked you down\nPick yourself up off the ground\nBrass and strings begin to swell\nEvery hero has a tale to tell"},
    {"title": "Dil Ki Baat", "artist_name": "Veer Kapoor", "language": "Hindi", "genre": "pop", "mood": "romantic", "bpm": 90, "duration": 28,
     "lyrics": "Dil ki baat sunata hoon\nTere pyaar mein kho jaata hoon\nSoft piano aur taron ki raat\nTere bina adhuri hai baat"},
    {"title": "Tanha Raatein", "artist_name": "Veer Kapoor", "language": "Hindi", "genre": "pop", "mood": "sad", "bpm": 72, "duration": 28,
     "lyrics": "Tanha raatein guzar rahi hain\nYaadein teri sataa rahi hain\nPiano ke sur mein dard hai\nHar dhun mein teri yaad hai"},
    {"title": "Prem Geet", "artist_name": "Meera Sharma", "language": "Hindi", "genre": "world", "mood": "romantic", "bpm": 85, "duration": 28,
     "lyrics": "Prem geet gaati hoon main\nDil ki baatein sunati hoon main\nSitar ki dhun mein pyaar hai\nHar sur mein tera intezaar hai"},
    {"title": "Nachle", "artist_name": "Priya Singh", "language": "Hindi", "genre": "pop", "mood": "energetic", "bpm": 128, "duration": 28,
     "lyrics": "Nachle nachle saari raat\nDhol baje aur ho barsaat\nPairo mein hai josh aaj\nDance floor pe karein raaj"},
    {"title": "Judai", "artist_name": "Raj Malhotra", "language": "Hindi", "genre": "world", "mood": "sad", "bpm": 68, "duration": 28,
     "lyrics": "Judai ka dard sehna pada\nHar pal mein gham rehna pada\nHarmonium ki awaaz mein\nDil ka dard chehna pada"},
    {"title": "Neeli Raat", "artist_name": "Anika", "language": "Hindi", "genre": "lofi", "mood": "calm", "bpm": 80, "duration": 28,
     "lyrics": "Neeli raat ka saaya hai\nLofi beats ne ghar basaya hai\nSitar ke sample dheere dheere\nPadhai ki raatein, sapne mere"},
    {"title": "Violet Hour", "artist_name": "Luna Ray", "language": "English", "genre": "chillwave", "mood": "sad", "bpm": 76, "duration": 28,
     "lyrics": "The violet hour between the day and dark\nMelancholic synths leave their mark\nDriving alone on empty streets\nWhere the night and sadness meets"},
    {"title": "Wildfire", "artist_name": "Kai Storm", "language": "English", "genre": "rock", "mood": "dramatic", "bpm": 130, "duration": 28,
     "lyrics": "Wildfire spreading through my veins\nBreaking free from all these chains\nPowerful chords shake the earth\nDestruction leading to rebirth"},
    {"title": "Rang De", "artist_name": "Priya Singh", "language": "Hindi", "genre": "pop", "mood": "happy", "bpm": 115, "duration": 28,
     "lyrics": "Rang de rang de duniya ko\nHar rung mein rang do saari galiyon ko\nLaal peela hara neela\nZindagi ka rang rangeela"},
]


class Command(BaseCommand):
    help = "Seed the database with sample track metadata"

    def handle(self, *args, **options):
        created = 0
        for t in SAMPLE_TRACKS:
            if Track.objects.filter(title=t["title"]).exists():
                continue
            genre = Genre.objects.filter(slug=t["genre"]).first()
            mood = Mood.objects.filter(slug=t["mood"]).first()
            Track.objects.create(
                title=t["title"],
                artist_name=t["artist_name"],
                language=t["language"],
                genre=genre,
                mood=mood,
                bpm=t["bpm"],
                duration=t["duration"],
                lyrics=t.get("lyrics", ""),
                description=f"AI-generated {t['genre']} track by {t['artist_name']}",
                tags=f"{t['genre']}, {t['mood']}",
                is_active=True,
                is_featured=(created % 4 == 0),
            )
            created += 1
            self.stdout.write(f"  Created: {t['title']} by {t['artist_name']}")
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} tracks (total: {Track.objects.count()})"))
