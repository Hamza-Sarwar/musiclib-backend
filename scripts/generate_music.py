"""
🎵 AI Music Generator using Meta's MusicGen

OPTION 1: Run locally (needs GPU with 8GB+ VRAM)
    pip install transformers torch scipy

OPTION 2: Run on Google Colab (FREE)
    1. Go to colab.research.google.com
    2. Create new notebook
    3. Change runtime to T4 GPU (Runtime > Change runtime type > T4 GPU)
    4. Copy this script into a cell and run it

The script generates music from text prompts and saves as WAV files.
You can then upload these to your Django admin.
"""

import os
import json
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
    # Classical
    {
        "prompt": "beautiful classical piano solo, romantic, expressive, Chopin style",
        "title": "Moonlit Sonata",
        "genre": "classical",
        "mood": "romantic",
        "bpm": 80,
    },
    # Chillwave
    {
        "prompt": "chillwave synth, retro 80s vibes, reverb, dreamy vocal chops, nostalgic",
        "title": "Retrowave Memories",
        "genre": "chillwave",
        "mood": "relaxing",
        "bpm": 92,
    },
    # World
    {
        "prompt": "middle eastern inspired music, oud, darbuka, atmospheric, mystical",
        "title": "Desert Caravan",
        "genre": "world",
        "mood": "mysterious",
        "bpm": 105,
    },
    # More variety
    {
        "prompt": "dark electronic ambient, deep bass, minimal, suspenseful, cyberpunk",
        "title": "Shadow Protocol",
        "genre": "electronic",
        "mood": "dark",
        "bpm": 90,
    },
    {
        "prompt": "playful quirky music, marimba, pizzicato strings, fun cartoon vibes",
        "title": "Bubble Pop Adventure",
        "genre": "acoustic",
        "mood": "playful",
        "bpm": 125,
    },
    {
        "prompt": "dramatic orchestral buildup, tension, suspense, powerful climax, movie trailer",
        "title": "The Final Stand",
        "genre": "cinematic",
        "mood": "dramatic",
        "bpm": 145,
    },
]

# ── Output directory ───────────────────────────────────────
OUTPUT_DIR = "generated_tracks"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_tracks(duration_seconds=30):
    """
    Generate all tracks using MusicGen.
    
    Args:
        duration_seconds: Length of each track (30s default, max ~30s for free model)
    """
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
    import torch
    import scipy.io.wavfile

    print("🔄 Loading MusicGen model (this takes a minute on first run)...")
    
    # Use "small" for faster generation, "medium" for better quality
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    
    # Move to GPU if available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    print(f"✅ Model loaded on {device}")

    # Set generation length (256 tokens ≈ 5 seconds at 32kHz)
    max_tokens = int(duration_seconds * 51.2)  # ~51.2 tokens per second

    metadata_list = []

    for i, track_info in enumerate(TRACK_PROMPTS):
        print(f"\n🎵 [{i+1}/{len(TRACK_PROMPTS)}] Generating: {track_info['title']}")
        print(f"   Prompt: {track_info['prompt'][:60]}...")

        # Generate
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

        # Save WAV file
        sampling_rate = model.config.audio_encoder.sampling_rate
        audio_data = audio_values[0, 0].cpu().numpy()
        
        filename = f"{track_info['genre']}_{track_info['title'].lower().replace(' ', '_')}.wav"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        scipy.io.wavfile.write(filepath, rate=sampling_rate, data=audio_data)
        
        # Calculate actual duration
        actual_duration = len(audio_data) / sampling_rate

        # Save metadata
        metadata = {
            "filename": filename,
            "title": track_info["title"],
            "genre": track_info["genre"],
            "mood": track_info["mood"],
            "bpm": track_info["bpm"],
            "duration": int(actual_duration),
            "prompt": track_info["prompt"],
        }
        metadata_list.append(metadata)
        
        print(f"   ✅ Saved: {filepath} ({actual_duration:.1f}s)")

    # Save metadata JSON (useful for bulk importing to Django)
    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata_list, f, indent=2)
    
    print(f"\n🎉 Done! Generated {len(metadata_list)} tracks in '{OUTPUT_DIR}/'")
    print(f"📄 Metadata saved to '{meta_path}'")
    print(f"\nNext steps:")
    print(f"  1. Convert WAV to MP3: ffmpeg -i input.wav -b:a 192k output.mp3")
    print(f"  2. Upload tracks via Django admin: http://localhost:8000/admin/")


if __name__ == "__main__":
    generate_tracks(duration_seconds=30)
