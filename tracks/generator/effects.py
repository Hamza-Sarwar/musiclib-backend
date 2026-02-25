import math


def low_pass_filter(samples, cutoff=1000.0, sr=22050):
    rc = 1.0 / (2.0 * math.pi * cutoff)
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    result = [0.0] * len(samples)
    result[0] = alpha * samples[0]
    for i in range(1, len(samples)):
        result[i] = result[i - 1] + alpha * (samples[i] - result[i - 1])
    return result


def simple_reverb(samples, sr=22050, decay=0.3, mix=0.25):
    delay_ms = [23, 37, 53, 71]
    delays = [int(d * sr / 1000) for d in delay_ms]
    result = list(samples)
    n = len(samples)
    for delay in delays:
        tap_decay = decay * (delays[0] / delay) ** 0.5
        for i in range(delay, n):
            result[i] += samples[i - delay] * tap_decay
    peak = max(abs(s) for s in result) if result else 1.0
    if peak > 1.0:
        result = [s / peak for s in result]
    return [samples[i] * (1.0 - mix) + result[i] * mix for i in range(n)]


def distortion(samples, gain=2.0):
    return [math.tanh(gain * s) for s in samples]


def bitcrush(samples, bits=8):
    levels = 2 ** bits
    return [round(s * levels) / levels for s in samples]
