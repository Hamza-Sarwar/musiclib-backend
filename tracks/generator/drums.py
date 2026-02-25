import math
import random

from .oscillators import sine_wave, white_noise
from .envelopes import adsr_envelope, apply_envelope
from .effects import low_pass_filter


def kick(sr=22050):
    duration = 0.15
    num_samples = int(sr * duration)
    samples = []
    for i in range(num_samples):
        t = i / sr
        freq = 150.0 * math.exp(-30.0 * t) + 50.0
        samples.append(math.sin(2 * math.pi * freq * t))
    env = adsr_envelope(num_samples, attack=0.002, decay=0.1, sustain=0.0, release=0.05, sr=sr)
    return apply_envelope(samples, env)


def snare(sr=22050):
    duration = 0.15
    num_samples = int(sr * duration)
    tone = sine_wave(200, duration, sr)
    noise = white_noise(duration, sr)
    mixed = [tone[i] * 0.4 + noise[i] * 0.6 for i in range(num_samples)]
    env = adsr_envelope(num_samples, attack=0.001, decay=0.08, sustain=0.0, release=0.06, sr=sr)
    return apply_envelope(mixed, env)


def hihat_closed(sr=22050):
    duration = 0.05
    num_samples = int(sr * duration)
    noise = white_noise(duration, sr)
    filtered = low_pass_filter(noise, cutoff=8000, sr=sr)
    env = adsr_envelope(num_samples, attack=0.001, decay=0.03, sustain=0.0, release=0.02, sr=sr)
    return apply_envelope(filtered, env)


def hihat_open(sr=22050):
    duration = 0.15
    num_samples = int(sr * duration)
    noise = white_noise(duration, sr)
    filtered = low_pass_filter(noise, cutoff=9000, sr=sr)
    env = adsr_envelope(num_samples, attack=0.001, decay=0.08, sustain=0.1, release=0.06, sr=sr)
    return apply_envelope(filtered, env)


def clap(sr=22050):
    duration = 0.12
    num_samples = int(sr * duration)
    result = [0.0] * num_samples
    for burst in range(3):
        offset = int(burst * 0.01 * sr)
        burst_len = int(0.02 * sr)
        noise = white_noise(0.02, sr)
        for i in range(min(burst_len, num_samples - offset)):
            result[offset + i] += noise[i] * 0.5
    env = adsr_envelope(num_samples, attack=0.001, decay=0.06, sustain=0.0, release=0.05, sr=sr)
    return apply_envelope(result, env)


DRUM_SOUNDS = {
    "K": kick,
    "S": snare,
    "H": hihat_closed,
    "O": hihat_open,
    "C": clap,
}


def sequence_drums(patterns, bpm, duration, sr=22050, swing=0.0):
    num_samples = int(sr * duration)
    output = [0.0] * num_samples
    beat_duration = 60.0 / bpm
    step_duration = beat_duration / 4  # 16th notes

    sound_cache = {}

    for instrument_key, pattern in patterns.items():
        if instrument_key not in DRUM_SOUNDS:
            continue
        if instrument_key not in sound_cache:
            sound_cache[instrument_key] = DRUM_SOUNDS[instrument_key](sr)
        sound = sound_cache[instrument_key]

        pattern_len = len(pattern)
        step = 0
        current_time = 0.0

        while current_time < duration:
            pattern_idx = step % pattern_len
            char = pattern[pattern_idx]

            if char == "x":
                sample_offset = int(current_time * sr)
                for j in range(len(sound)):
                    idx = sample_offset + j
                    if idx < num_samples:
                        output[idx] += sound[j]

            swing_offset = swing * step_duration * 0.5 if step % 2 == 1 else 0.0
            current_time += step_duration + swing_offset
            step += 1

    return output
