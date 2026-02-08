"""
Auto-Metadata Script

Analyzes audio files to detect BPM and generate waveform peak data.
Uses librosa for audio analysis.

Usage:
    python scripts/auto_metadata.py generated_tracks/
    python scripts/auto_metadata.py generated_tracks/ --peaks 200
"""

import os
import sys
import json
import argparse


def detect_bpm(file_path):
    """Detect BPM of an audio file using librosa."""
    import librosa
    import numpy as np

    y, sr = librosa.load(file_path, sr=22050, mono=True)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return int(round(float(np.asarray(tempo).flat[0])))


def generate_peaks(file_path, num_peaks=200):
    """Generate waveform peaks for visualization."""
    import librosa
    import numpy as np

    y, sr = librosa.load(file_path, sr=22050, mono=True)

    # Normalize
    max_val = np.max(np.abs(y))
    if max_val > 0:
        y = y / max_val

    # Downsample to num_peaks
    chunk_size = max(1, len(y) // num_peaks)
    peaks = []
    for i in range(0, len(y), chunk_size):
        chunk = y[i : i + chunk_size]
        peaks.append(round(float(np.max(np.abs(chunk))), 4))

    return peaks[:num_peaks]


def process_directory(directory, num_peaks=200):
    """Process all audio files in a directory."""
    meta_path = os.path.join(directory, "metadata.json")

    if not os.path.exists(meta_path):
        print(f"Error: metadata.json not found in {directory}")
        sys.exit(1)

    with open(meta_path, "r") as f:
        metadata_list = json.load(f)

    updated = 0
    for meta in metadata_list:
        file_path = os.path.join(directory, meta["filename"])
        if not os.path.exists(file_path):
            print(f"  Skipped (not found): {meta['filename']}")
            continue

        print(f"  Analyzing: {meta['title']}...")

        try:
            # Detect BPM
            detected_bpm = detect_bpm(file_path)
            meta["detected_bpm"] = detected_bpm
            # Update BPM if it seems more accurate
            if abs(detected_bpm - meta.get("bpm", 0)) > 20:
                print(f"    BPM: {meta.get('bpm')} -> {detected_bpm} (detected)")

            # Generate waveform peaks
            peaks = generate_peaks(file_path, num_peaks)
            meta["waveform_data"] = peaks
            print(f"    Waveform: {len(peaks)} peaks generated")

            updated += 1
        except Exception as e:
            print(f"    Error: {e}")

    # Save updated metadata
    with open(meta_path, "w") as f:
        json.dump(metadata_list, f, indent=2)

    print(f"\nDone! Updated {updated}/{len(metadata_list)} tracks")
    print(f"Metadata saved to '{meta_path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-detect BPM and generate waveform data")
    parser.add_argument("directory", help="Path to generated_tracks directory")
    parser.add_argument("--peaks", type=int, default=200, help="Number of waveform peaks (default: 200)")
    args = parser.parse_args()

    process_directory(args.directory, args.peaks)
