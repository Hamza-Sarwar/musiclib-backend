"""
Management command to generate waveform peak data for tracks that don't have it.

Usage:
    python manage.py generate_waveforms
"""
import struct
import wave
from django.core.management.base import BaseCommand
from tracks.models import Track


def compute_peaks(file_path, num_peaks=200):
    """Compute waveform peaks from an audio file."""
    try:
        # Try reading as WAV first
        with wave.open(file_path, "rb") as wf:
            n_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            n_frames = wf.getnframes()
            frames = wf.readframes(n_frames)

        # Determine format string based on sample width
        fmt = {1: "b", 2: "h", 4: "i"}.get(sample_width)
        if not fmt:
            return None

        samples = struct.unpack(f"<{n_frames * n_channels}{fmt}", frames)

        # Mix down to mono by averaging channels
        if n_channels > 1:
            samples = [
                sum(samples[i : i + n_channels]) / n_channels
                for i in range(0, len(samples), n_channels)
            ]

        # Normalize
        max_val = max(abs(s) for s in samples) or 1
        normalized = [s / max_val for s in samples]

        # Downsample to num_peaks
        chunk_size = max(1, len(normalized) // num_peaks)
        peaks = []
        for i in range(0, len(normalized), chunk_size):
            chunk = normalized[i : i + chunk_size]
            peaks.append(round(max(abs(s) for s in chunk), 4))

        return peaks[:num_peaks]
    except Exception:
        return None


class Command(BaseCommand):
    help = "Generate waveform peak data for tracks missing it"

    def handle(self, *args, **options):
        tracks = Track.objects.filter(waveform_data__isnull=True, is_active=True)
        total = tracks.count()
        self.stdout.write(f"Found {total} tracks without waveform data")

        generated = 0
        for track in tracks:
            try:
                peaks = compute_peaks(track.audio_file.path)
                if peaks:
                    track.waveform_data = peaks
                    track.save(update_fields=["waveform_data"])
                    generated += 1
                    self.stdout.write(f"  Generated: {track.title}")
                else:
                    self.stdout.write(f"  Skipped (unsupported format): {track.title}")
            except Exception as e:
                self.stderr.write(f"  Error for {track.title}: {e}")

        self.stdout.write(
            self.style.SUCCESS(f"\nDone: {generated}/{total} waveforms generated")
        )
