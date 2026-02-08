"""
Local AI Music Generator using Meta's MusicGen (no API needed).
Uses MPS (Apple Silicon GPU) when available for faster generation.

Usage:
    python scripts/generate_local.py --count 5
    python scripts/generate_local.py --count 10 --duration 20
    python scripts/generate_local.py --resume
"""

import os
import sys
import json
import argparse

TRACK_PROMPTS = [
    {"prompt": "calm lofi hip hop beat, vinyl crackle, soft piano, mellow drums, study music",
     "title": "Midnight Study Session", "genre": "lofi", "mood": "calm", "bpm": 85},
    {"prompt": "cozy lofi beat, gentle guitar melody, rain sounds, warm atmosphere",
     "title": "Rainy Day Coffee", "genre": "lofi", "mood": "relaxing", "bpm": 78},
    {"prompt": "ambient atmospheric pad, ethereal synth, slow evolving texture, meditation music",
     "title": "Floating in Space", "genre": "ambient", "mood": "peaceful", "bpm": 60},
    {"prompt": "upbeat corporate background music, positive, motivational, acoustic guitar, light drums",
     "title": "Success Story", "genre": "corporate", "mood": "upbeat", "bpm": 120},
    {"prompt": "epic cinematic orchestral music, dramatic strings, powerful brass, film score",
     "title": "Rise of Heroes", "genre": "cinematic", "mood": "epic", "bpm": 130},
    {"prompt": "chill electronic beat, soft synths, gentle bassline, dreamy atmosphere",
     "title": "Neon Dreams", "genre": "electronic", "mood": "relaxing", "bpm": 100},
    {"prompt": "gentle acoustic guitar fingerpicking, warm, intimate, folk inspired",
     "title": "Morning Light", "genre": "acoustic", "mood": "peaceful", "bpm": 90},
    {"prompt": "smooth jazz, saxophone melody, soft piano chords, brushed drums, late night",
     "title": "Blue Velvet Lounge", "genre": "jazz", "mood": "calm", "bpm": 95},
    {"prompt": "beautiful classical piano solo, romantic, expressive, Chopin style",
     "title": "Moonlit Sonata", "genre": "classical", "mood": "romantic", "bpm": 80},
    {"prompt": "dark electronic ambient, deep bass, minimal, suspenseful, cyberpunk",
     "title": "Shadow Protocol", "genre": "electronic", "mood": "dark", "bpm": 90},
    {"prompt": "emotional cinematic piano, soft strings, melancholic, film soundtrack, beautiful",
     "title": "Farewell Letter", "genre": "cinematic", "mood": "sad", "bpm": 72},
    {"prompt": "happy acoustic ukulele, clapping, whistling, cheerful summer vibes",
     "title": "Sunny Afternoon", "genre": "acoustic", "mood": "happy", "bpm": 115},
    {"prompt": "deep ambient drone, nature sounds, wind, peaceful atmosphere, sleep music",
     "title": "Deep Forest Dawn", "genre": "ambient", "mood": "calm", "bpm": 55},
    {"prompt": "synthwave retro electronic, 80s inspired, driving arpeggios, neon aesthetic",
     "title": "Midnight Drive", "genre": "electronic", "mood": "energetic", "bpm": 118},
    {"prompt": "middle eastern inspired music, oud, darbuka, atmospheric, mystical",
     "title": "Desert Caravan", "genre": "world", "mood": "mysterious", "bpm": 105},
    {"prompt": "chill hip hop beat, smooth bass, Rhodes piano, head nodding groove",
     "title": "City Lights Flow", "genre": "hip-hop", "mood": "calm", "bpm": 88},
    {"prompt": "chillwave synth, retro 80s vibes, reverb, dreamy vocal chops, nostalgic",
     "title": "Retrowave Memories", "genre": "chillwave", "mood": "relaxing", "bpm": 92},
    {"prompt": "inspiring corporate music, piano, strings, building energy, presentation background",
     "title": "Innovation Drive", "genre": "corporate", "mood": "inspiring", "bpm": 110},
    {"prompt": "upbeat jazz swing, walking bass, piano, bright trumpet, energetic",
     "title": "Downtown Stride", "genre": "jazz", "mood": "upbeat", "bpm": 140},
    {"prompt": "catchy pop instrumental, bright synths, four on the floor beat, summer hit",
     "title": "Summer Crush", "genre": "pop", "mood": "happy", "bpm": 120},
]

OUTPUT_DIR = "generated_tracks"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate(duration_seconds=20, count=None, resume=False):
    import torch
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import scipy.io.wavfile

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    metadata_list = []
    existing_titles = set()

    if resume and os.path.exists(meta_path):
        with open(meta_path, "r") as f:
            metadata_list = json.load(f)
            existing_titles = {m["title"] for m in metadata_list}
        print(f"Resuming: {len(existing_titles)} tracks already generated")

    # Use CPU on Intel Macs (MPS only works well on Apple Silicon)
    device = "cpu"

    print(f"Loading MusicGen model on {device}...")
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    model = model.to(device)
    print("Model loaded!")

    max_tokens = int(duration_seconds * 51.2)
    prompts = TRACK_PROMPTS[:count] if count else TRACK_PROMPTS
    generated = 0

    for i, track_info in enumerate(prompts):
        if resume and track_info["title"] in existing_titles:
            print(f"[{i+1}/{len(prompts)}] Skipping (exists): {track_info['title']}")
            continue

        print(f"\n[{i+1}/{len(prompts)}] Generating: {track_info['title']}")
        print(f"   Prompt: {track_info['prompt'][:60]}...")

        try:
            inputs = processor(
                text=[track_info["prompt"]],
                padding=True,
                return_tensors="pt",
            ).to(device)

            audio_values = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                guidance_scale=3.0,
            )

            sampling_rate = model.config.audio_encoder.sampling_rate
            audio_data = audio_values[0, 0].cpu().numpy()

            base_name = f"{track_info['genre']}_{track_info['title'].lower().replace(' ', '_')}"
            wav_filename = f"{base_name}.wav"
            wav_path = os.path.join(OUTPUT_DIR, wav_filename)

            scipy.io.wavfile.write(wav_path, rate=sampling_rate, data=audio_data)

            actual_duration = len(audio_data) / sampling_rate
            file_size = os.path.getsize(wav_path)

            metadata = {
                "filename": wav_filename,
                "title": track_info["title"],
                "genre": track_info["genre"],
                "mood": track_info["mood"],
                "bpm": track_info["bpm"],
                "duration": int(actual_duration),
                "prompt": track_info["prompt"],
            }
            metadata_list.append(metadata)
            generated += 1

            # Save after each track
            with open(meta_path, "w") as f:
                json.dump(metadata_list, f, indent=2)

            print(f"   Saved: {wav_filename} ({file_size // 1024} KB, {actual_duration:.1f}s)")

        except Exception as e:
            print(f"   ERROR: {e}")
            continue

    print(f"\nDone! Generated {generated} new tracks ({len(metadata_list)} total)")


def import_to_django():
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

    import django
    django.setup()

    from django.core.files import File
    from tracks.models import Track, Genre, Mood

    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    if not os.path.exists(meta_path):
        print("No metadata.json found.")
        return

    with open(meta_path, "r") as f:
        metadata_list = json.load(f)

    imported = 0
    for meta in metadata_list:
        filepath = os.path.join(OUTPUT_DIR, meta["filename"])
        if not os.path.exists(filepath):
            continue
        if Track.objects.filter(title=meta["title"]).exists():
            print(f"  Skipping {meta['title']}: already exists")
            continue

        genre = Genre.objects.filter(slug=meta["genre"]).first()
        mood = Mood.objects.filter(slug=meta["mood"]).first()

        with open(filepath, "rb") as audio_file:
            track = Track(
                title=meta["title"],
                genre=genre,
                mood=mood,
                bpm=meta.get("bpm"),
                duration=meta.get("duration", 20),
                description=meta.get("prompt", ""),
                tags=f"{meta['genre']}, {meta['mood']}",
                is_active=True,
                is_featured=(imported % 3 == 0),
            )
            track.audio_file.save(meta["filename"], File(audio_file), save=True)

        print(f"  Imported: {meta['title']} ({meta['genre']} / {meta['mood']})")
        imported += 1

    print(f"\nImported {imported} tracks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate music locally with MusicGen")
    parser.add_argument("--duration", type=int, default=20, help="Duration in seconds (default: 20)")
    parser.add_argument("--count", type=int, default=None, help="Number of tracks (default: all 20)")
    parser.add_argument("--resume", action="store_true", help="Skip existing tracks")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Import to Django after")
    parser.add_argument("--import-only", action="store_true", help="Only import, no generation")
    args = parser.parse_args()

    if args.import_only:
        import_to_django()
    else:
        generate(duration_seconds=args.duration, count=args.count, resume=args.resume)
        if args.do_import:
            import_to_django()
