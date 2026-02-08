"""
AI Music Generator using Replicate API (MusicGen in the cloud)

No GPU needed - runs Meta's MusicGen model via Replicate's API.

Setup:
    pip install replicate
    export REPLICATE_API_TOKEN=r8_your_token_here

Usage:
    python scripts/generate_music.py
    python scripts/generate_music.py --duration 15 --count 5
    python scripts/generate_music.py --resume
    python scripts/generate_music.py --import  # Generate + auto-import to Django
"""

import os
import sys
import json
import time
import argparse
import urllib.request
from datetime import datetime

# ── Prompts for generating diverse tracks ──────────────────
TRACK_PROMPTS = [
    # Lo-Fi
    {
        "prompt": "calm lofi hip hop beat, vinyl crackle, soft piano, mellow drums, study music",
        "title": "Midnight Study Session",
        "genre": "lofi",
        "mood": "calm",
        "bpm": 85,
    },
    {
        "prompt": "cozy lofi beat, gentle guitar melody, rain sounds, warm atmosphere",
        "title": "Rainy Day Coffee",
        "genre": "lofi",
        "mood": "relaxing",
        "bpm": 78,
    },
    {
        "prompt": "lofi chill beat, soft rhodes piano, tape hiss, lazy afternoon vibes",
        "title": "Sunday Slow Down",
        "genre": "lofi",
        "mood": "peaceful",
        "bpm": 72,
    },
    {
        "prompt": "lofi hip hop, dusty samples, jazz piano chops, boom bap drums",
        "title": "Old School Daydream",
        "genre": "lofi",
        "mood": "relaxing",
        "bpm": 82,
    },
    # Ambient
    {
        "prompt": "ambient atmospheric pad, ethereal synth, slow evolving texture, meditation music",
        "title": "Floating in Space",
        "genre": "ambient",
        "mood": "peaceful",
        "bpm": 60,
    },
    {
        "prompt": "deep ambient drone, nature sounds, wind, peaceful atmosphere, sleep music",
        "title": "Deep Forest Dawn",
        "genre": "ambient",
        "mood": "calm",
        "bpm": 55,
    },
    {
        "prompt": "ambient soundscape, crystal singing bowls, soft reverb, healing meditation",
        "title": "Crystal Healing",
        "genre": "ambient",
        "mood": "peaceful",
        "bpm": 50,
    },
    {
        "prompt": "ambient pad, underwater sounds, deep ocean atmosphere, mysterious calm",
        "title": "Ocean Depths",
        "genre": "ambient",
        "mood": "mysterious",
        "bpm": 45,
    },
    # Corporate
    {
        "prompt": "upbeat corporate background music, positive, motivational, acoustic guitar, light drums",
        "title": "Success Story",
        "genre": "corporate",
        "mood": "upbeat",
        "bpm": 120,
    },
    {
        "prompt": "inspiring corporate music, piano, strings, building energy, presentation background",
        "title": "Innovation Drive",
        "genre": "corporate",
        "mood": "inspiring",
        "bpm": 110,
    },
    {
        "prompt": "clean corporate background, light piano, positive vibe, technology presentation",
        "title": "Tech Forward",
        "genre": "corporate",
        "mood": "upbeat",
        "bpm": 115,
    },
    {
        "prompt": "warm corporate music, gentle strings, hopeful, startup video background",
        "title": "New Horizons",
        "genre": "corporate",
        "mood": "inspiring",
        "bpm": 105,
    },
    # Cinematic
    {
        "prompt": "epic cinematic orchestral music, dramatic strings, powerful brass, film score",
        "title": "Rise of Heroes",
        "genre": "cinematic",
        "mood": "epic",
        "bpm": 130,
    },
    {
        "prompt": "emotional cinematic piano, soft strings, melancholic, film soundtrack, beautiful",
        "title": "Farewell Letter",
        "genre": "cinematic",
        "mood": "sad",
        "bpm": 72,
    },
    {
        "prompt": "dramatic orchestral buildup, tension, suspense, powerful climax, movie trailer",
        "title": "The Final Stand",
        "genre": "cinematic",
        "mood": "dramatic",
        "bpm": 145,
    },
    {
        "prompt": "cinematic adventure music, full orchestra, heroic theme, fantasy film score",
        "title": "Quest Begins",
        "genre": "cinematic",
        "mood": "epic",
        "bpm": 135,
    },
    {
        "prompt": "tender cinematic music, solo cello, emotional, documentary background",
        "title": "Gentle Memories",
        "genre": "cinematic",
        "mood": "romantic",
        "bpm": 68,
    },
    # Electronic
    {
        "prompt": "chill electronic beat, soft synths, gentle bassline, dreamy atmosphere",
        "title": "Neon Dreams",
        "genre": "electronic",
        "mood": "relaxing",
        "bpm": 100,
    },
    {
        "prompt": "energetic electronic dance music, driving beat, synth lead, festival energy",
        "title": "Digital Sunrise",
        "genre": "electronic",
        "mood": "energetic",
        "bpm": 128,
    },
    {
        "prompt": "dark electronic ambient, deep bass, minimal, suspenseful, cyberpunk",
        "title": "Shadow Protocol",
        "genre": "electronic",
        "mood": "dark",
        "bpm": 90,
    },
    {
        "prompt": "future bass, warm chords, melodic drops, euphoric energy, summer festival",
        "title": "Golden Hour",
        "genre": "electronic",
        "mood": "happy",
        "bpm": 150,
    },
    {
        "prompt": "synthwave retro electronic, 80s inspired, driving arpeggios, neon aesthetic",
        "title": "Midnight Drive",
        "genre": "electronic",
        "mood": "energetic",
        "bpm": 118,
    },
    {
        "prompt": "deep house, groovy bassline, warm pads, late night club atmosphere",
        "title": "After Hours",
        "genre": "electronic",
        "mood": "relaxing",
        "bpm": 122,
    },
    # Acoustic
    {
        "prompt": "gentle acoustic guitar fingerpicking, warm, intimate, folk inspired",
        "title": "Morning Light",
        "genre": "acoustic",
        "mood": "peaceful",
        "bpm": 90,
    },
    {
        "prompt": "happy acoustic ukulele, clapping, whistling, cheerful summer vibes",
        "title": "Sunny Afternoon",
        "genre": "acoustic",
        "mood": "happy",
        "bpm": 115,
    },
    {
        "prompt": "playful quirky music, marimba, pizzicato strings, fun cartoon vibes",
        "title": "Bubble Pop Adventure",
        "genre": "acoustic",
        "mood": "playful",
        "bpm": 125,
    },
    {
        "prompt": "soft acoustic guitar, campfire atmosphere, warm folk ballad, evening sky",
        "title": "Campfire Stories",
        "genre": "acoustic",
        "mood": "calm",
        "bpm": 88,
    },
    {
        "prompt": "uplifting acoustic guitar and piano, positive energy, travel vlog music",
        "title": "Open Road",
        "genre": "acoustic",
        "mood": "inspiring",
        "bpm": 108,
    },
    # Jazz
    {
        "prompt": "smooth jazz, saxophone melody, soft piano chords, brushed drums, late night",
        "title": "Blue Velvet Lounge",
        "genre": "jazz",
        "mood": "calm",
        "bpm": 95,
    },
    {
        "prompt": "upbeat jazz swing, walking bass, piano, bright trumpet, energetic",
        "title": "Downtown Stride",
        "genre": "jazz",
        "mood": "upbeat",
        "bpm": 140,
    },
    {
        "prompt": "bossa nova jazz, nylon guitar, light percussion, smooth saxophone, tropical",
        "title": "Rio Sunset",
        "genre": "jazz",
        "mood": "relaxing",
        "bpm": 100,
    },
    {
        "prompt": "jazz trio, upright bass, piano improvisation, brushes on snare, intimate club",
        "title": "Late Night Set",
        "genre": "jazz",
        "mood": "calm",
        "bpm": 110,
    },
    # Classical
    {
        "prompt": "beautiful classical piano solo, romantic, expressive, Chopin style",
        "title": "Moonlit Sonata",
        "genre": "classical",
        "mood": "romantic",
        "bpm": 80,
    },
    {
        "prompt": "classical string quartet, elegant, refined, baroque inspired, chamber music",
        "title": "Royal Gardens",
        "genre": "classical",
        "mood": "peaceful",
        "bpm": 76,
    },
    {
        "prompt": "classical orchestral, dramatic crescendo, powerful timpani, full symphony",
        "title": "Storm Symphony",
        "genre": "classical",
        "mood": "dramatic",
        "bpm": 120,
    },
    # Hip Hop
    {
        "prompt": "chill hip hop beat, smooth bass, Rhodes piano, head nodding groove",
        "title": "City Lights Flow",
        "genre": "hip-hop",
        "mood": "calm",
        "bpm": 88,
    },
    {
        "prompt": "dark trap beat, heavy 808 bass, hi hats, atmospheric pads, hard hitting",
        "title": "Night Prowler",
        "genre": "hip-hop",
        "mood": "dark",
        "bpm": 140,
    },
    {
        "prompt": "upbeat hip hop, energetic drums, brass stabs, party vibe, celebration",
        "title": "Victory Lap",
        "genre": "hip-hop",
        "mood": "energetic",
        "bpm": 95,
    },
    # Pop
    {
        "prompt": "catchy pop instrumental, bright synths, four on the floor beat, summer hit",
        "title": "Summer Crush",
        "genre": "pop",
        "mood": "happy",
        "bpm": 120,
    },
    {
        "prompt": "dreamy pop, reverb guitars, soft vocals, indie aesthetic, nostalgic",
        "title": "Pastel Skies",
        "genre": "pop",
        "mood": "romantic",
        "bpm": 98,
    },
    # Rock
    {
        "prompt": "indie rock, jangly guitars, driving rhythm, upbeat energy, alternative",
        "title": "Electric Avenue",
        "genre": "rock",
        "mood": "energetic",
        "bpm": 135,
    },
    {
        "prompt": "post rock, atmospheric guitars, building dynamics, crescendo, emotional",
        "title": "Signal Fires",
        "genre": "rock",
        "mood": "dramatic",
        "bpm": 110,
    },
    # R&B
    {
        "prompt": "smooth rnb, silky synths, slow groove, romantic atmosphere, late night",
        "title": "Velvet Touch",
        "genre": "rnb",
        "mood": "romantic",
        "bpm": 75,
    },
    {
        "prompt": "modern rnb, atmospheric pads, trap percussion, moody, emotional",
        "title": "Moonlight Drive",
        "genre": "rnb",
        "mood": "calm",
        "bpm": 82,
    },
    # World
    {
        "prompt": "middle eastern inspired music, oud, darbuka, atmospheric, mystical",
        "title": "Desert Caravan",
        "genre": "world",
        "mood": "mysterious",
        "bpm": 105,
    },
    {
        "prompt": "african drums, kalimba, rhythmic percussion, joyful celebration, dance",
        "title": "Savanna Dance",
        "genre": "world",
        "mood": "happy",
        "bpm": 115,
    },
    {
        "prompt": "celtic folk, tin whistle, fiddle, bodhran drum, lively jig, Irish pub",
        "title": "Green Hills",
        "genre": "world",
        "mood": "upbeat",
        "bpm": 130,
    },
    {
        "prompt": "japanese traditional, koto, shakuhachi flute, zen garden, meditative",
        "title": "Zen Garden",
        "genre": "world",
        "mood": "peaceful",
        "bpm": 60,
    },
    # Chillwave
    {
        "prompt": "chillwave synth, retro 80s vibes, reverb, dreamy vocal chops, nostalgic",
        "title": "Retrowave Memories",
        "genre": "chillwave",
        "mood": "relaxing",
        "bpm": 92,
    },
    {
        "prompt": "chillwave, warm analog synths, hazy pads, sunset beach vibes, vapor",
        "title": "Analog Sunset",
        "genre": "chillwave",
        "mood": "peaceful",
        "bpm": 86,
    },
    {
        "prompt": "lo-fi chillwave, tape warble, dreamy chords, nostalgic summer",
        "title": "Polaroid Summer",
        "genre": "chillwave",
        "mood": "happy",
        "bpm": 94,
    },
]

# ── Output directory ───────────────────────────────────────
OUTPUT_DIR = "generated_tracks"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_tracks_replicate(duration_seconds=30, count=None, resume=False):
    """
    Generate tracks using Replicate API (MusicGen in the cloud).

    Args:
        duration_seconds: Length of each track
        count: Number of tracks to generate (None = all)
        resume: Skip tracks that already have files
    """
    import replicate

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    metadata_list = []
    existing_titles = set()

    if resume and os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            metadata_list = json.load(f)
            existing_titles = {m["title"] for m in metadata_list}
        print(f"Resuming: {len(existing_titles)} tracks already generated")

    prompts = TRACK_PROMPTS[:count] if count else TRACK_PROMPTS
    generated = 0

    for i, track_info in enumerate(prompts):
        if resume and track_info["title"] in existing_titles:
            print(f"[{i+1}/{len(prompts)}] Skipping (exists): {track_info['title']}")
            continue

        print(f"\n[{i+1}/{len(prompts)}] Generating: {track_info['title']}")
        print(f"   Prompt: {track_info['prompt'][:60]}...")

        try:
            output = replicate.run(
                "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
                input={
                    "prompt": track_info["prompt"],
                    "duration": duration_seconds,
                    "model_version": "stereo-melody-large",
                    "output_format": "wav",
                    "normalization_strategy": "peak",
                },
            )

            # output is a URL to the generated audio file
            audio_url = str(output)
            base_name = f"{track_info['genre']}_{track_info['title'].lower().replace(' ', '_')}"
            wav_filename = f"{base_name}.wav"
            wav_path = os.path.join(OUTPUT_DIR, wav_filename)

            print(f"   Downloading: {audio_url[:80]}...")
            urllib.request.urlretrieve(audio_url, wav_path)

            file_size = os.path.getsize(wav_path)
            print(f"   Saved: {wav_filename} ({file_size // 1024} KB)")

            metadata = {
                "filename": wav_filename,
                "title": track_info["title"],
                "genre": track_info["genre"],
                "mood": track_info["mood"],
                "bpm": track_info["bpm"],
                "duration": duration_seconds,
                "prompt": track_info["prompt"],
            }
            metadata_list.append(metadata)
            generated += 1

            # Save metadata after each track (in case of interruption)
            with open(meta_path, "w") as f:
                json.dump(metadata_list, f, indent=2)

        except Exception as e:
            print(f"   ERROR: {e}")
            print(f"   Skipping this track...")
            continue

        # Rate limit: wait between requests
        if i < len(prompts) - 1:
            print("   Waiting 12s (rate limit)...")
            time.sleep(12)

    print(f"\nDone! Generated {generated} new tracks ({len(metadata_list)} total) in '{OUTPUT_DIR}/'")
    print(f"Metadata saved to '{meta_path}'")
    print(f"\nNext step - import to Django:")
    print(f"  python manage.py import_tracks {OUTPUT_DIR}/")


def import_to_django():
    """Import generated tracks into Django database."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django
    django.setup()

    from django.core.files import File
    from tracks.models import Track, Genre, Mood

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    if not os.path.exists(meta_path):
        print("No metadata.json found. Run generation first.")
        return

    with open(meta_path, "r") as f:
        metadata_list = json.load(f)

    imported = 0
    for meta in metadata_list:
        filepath = os.path.join(OUTPUT_DIR, meta["filename"])
        if not os.path.exists(filepath):
            print(f"  Skipping {meta['title']}: file not found")
            continue

        if Track.objects.filter(title=meta["title"]).exists():
            print(f"  Skipping {meta['title']}: already in database")
            continue

        genre = Genre.objects.filter(slug=meta["genre"]).first()
        mood = Mood.objects.filter(slug=meta["mood"]).first()

        with open(filepath, "rb") as audio_file:
            track = Track(
                title=meta["title"],
                genre=genre,
                mood=mood,
                bpm=meta.get("bpm"),
                duration=meta.get("duration", 30),
                description=meta.get("prompt", ""),
                tags=f"{meta['genre']}, {meta['mood']}",
                is_active=True,
                is_featured=(imported % 3 == 0),  # Feature every 3rd track
            )
            track.audio_file.save(meta["filename"], File(audio_file), save=True)

        print(f"  Imported: {meta['title']} ({meta['genre']} / {meta['mood']})")
        imported += 1

    print(f"\nImported {imported} tracks into Django.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate AI music tracks via Replicate API")
    parser.add_argument("--duration", type=int, default=30, help="Track duration in seconds (default: 30)")
    parser.add_argument("--count", type=int, default=None, help="Number of tracks to generate (default: all)")
    parser.add_argument("--resume", action="store_true", help="Skip existing tracks")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import generated tracks to Django after generation")
    parser.add_argument("--import-only", action="store_true", help="Only import existing tracks (no generation)")
    args = parser.parse_args()

    if args.import_only:
        import_to_django()
    else:
        generate_tracks_replicate(
            duration_seconds=args.duration,
            count=args.count,
            resume=args.resume,
        )
        if args.do_import:
            import_to_django()
