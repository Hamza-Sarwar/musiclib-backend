import math
import random


def sine_wave(freq, duration, sr=22050, phase=0.0):
    num_samples = int(sr * duration)
    return [
        math.sin(2 * math.pi * freq * i / sr + phase)
        for i in range(num_samples)
    ]


def saw_wave(freq, duration, sr=22050):
    num_samples = int(sr * duration)
    samples = []
    period = sr / freq if freq > 0 else sr
    for i in range(num_samples):
        t = (i % period) / period
        samples.append(2.0 * t - 1.0)
    return samples


def square_wave(freq, duration, sr=22050):
    num_samples = int(sr * duration)
    samples = []
    period = sr / freq if freq > 0 else sr
    half = period / 2
    for i in range(num_samples):
        samples.append(1.0 if (i % period) < half else -1.0)
    return samples


def triangle_wave(freq, duration, sr=22050):
    num_samples = int(sr * duration)
    samples = []
    period = sr / freq if freq > 0 else sr
    for i in range(num_samples):
        t = (i % period) / period
        samples.append(4.0 * abs(t - 0.5) - 1.0)
    return samples


def pulse_wave(freq, duration, sr=22050, duty=0.25):
    num_samples = int(sr * duration)
    samples = []
    period = sr / freq if freq > 0 else sr
    threshold = period * duty
    for i in range(num_samples):
        samples.append(1.0 if (i % period) < threshold else -1.0)
    return samples


def white_noise(duration, sr=22050):
    num_samples = int(sr * duration)
    return [random.uniform(-1.0, 1.0) for _ in range(num_samples)]


def rich_tone(freq, duration, sr=22050, harmonics=None):
    if harmonics is None:
        harmonics = [(1, 1.0), (2, 0.5), (3, 0.25), (4, 0.125)]
    num_samples = int(sr * duration)
    samples = [0.0] * num_samples
    for harmonic_num, amplitude in harmonics:
        h_freq = freq * harmonic_num
        if h_freq >= sr / 2:
            continue
        for i in range(num_samples):
            samples[i] += amplitude * math.sin(2 * math.pi * h_freq * i / sr)
    peak = max(abs(s) for s in samples) if samples else 1.0
    if peak > 0:
        samples = [s / peak for s in samples]
    return samples
