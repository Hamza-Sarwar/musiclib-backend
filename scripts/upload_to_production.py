"""Upload locally generated audio files to production server."""
import json
import os
import sys
import requests

API_URL = os.environ.get("API_URL", "https://musiclib-api.onrender.com/api")
UPLOAD_SECRET = os.environ.get("UPLOAD_SECRET", "")
TRACKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generated_tracks")


def upload_all():
    if not UPLOAD_SECRET:
        print("ERROR: Set UPLOAD_SECRET env variable")
        sys.exit(1)

    metadata_path = os.path.join(TRACKS_DIR, "metadata.json")
    if not os.path.exists(metadata_path):
        print(f"ERROR: {metadata_path} not found")
        sys.exit(1)

    with open(metadata_path) as f:
        tracks = json.load(f)

    url = f"{API_URL}/tracks/upload-audio/"
    headers = {"X-Upload-Secret": UPLOAD_SECRET}

    uploaded = 0
    skipped = 0
    errors = 0

    for i, track in enumerate(tracks, 1):
        filepath = os.path.join(TRACKS_DIR, track["filename"])
        if not os.path.exists(filepath):
            print(f"  [{i}/{len(tracks)}] SKIP (no file): {track['title']}")
            skipped += 1
            continue

        print(f"  [{i}/{len(tracks)}] Uploading: {track['title']}...", end=" ", flush=True)

        try:
            with open(filepath, "rb") as audio:
                resp = requests.post(
                    url,
                    headers=headers,
                    data={
                        "title": track["title"],
                        "genre": track.get("genre", ""),
                        "mood": track.get("mood", ""),
                        "bpm": track.get("bpm", 0),
                        "duration": track.get("duration", 28),
                        "artist_name": track.get("artist_name", ""),
                        "language": track.get("language", "English"),
                        "lyrics": track.get("lyrics", ""),
                        "description": track.get("prompt", ""),
                    },
                    files={"audio": (track["filename"], audio, "audio/wav")},
                    timeout=120,
                )

            if resp.status_code == 200:
                print("OK")
                uploaded += 1
            else:
                print(f"ERROR {resp.status_code}: {resp.text[:100]}")
                errors += 1
        except Exception as e:
            print(f"ERROR: {e}")
            errors += 1

    print(f"\nDone! Uploaded: {uploaded}, Skipped: {skipped}, Errors: {errors}")


if __name__ == "__main__":
    upload_all()
