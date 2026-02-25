def adsr_envelope(num_samples, attack=0.01, decay=0.05, sustain=0.7, release=0.05, sr=22050):
    attack_samples = int(attack * sr)
    decay_samples = int(decay * sr)
    release_samples = int(release * sr)
    sustain_samples = max(0, num_samples - attack_samples - decay_samples - release_samples)

    env = []
    for i in range(min(attack_samples, num_samples - len(env))):
        env.append(i / max(attack_samples, 1))
    for i in range(min(decay_samples, num_samples - len(env))):
        env.append(1.0 - (1.0 - sustain) * (i / max(decay_samples, 1)))
    for _ in range(min(sustain_samples, num_samples - len(env))):
        env.append(sustain)
    for i in range(min(release_samples, num_samples - len(env))):
        env.append(sustain * (1.0 - i / max(release_samples, 1)))
    while len(env) < num_samples:
        env.append(0.0)
    return env[:num_samples]


def apply_envelope(samples, envelope):
    length = min(len(samples), len(envelope))
    return [samples[i] * envelope[i] for i in range(length)]


def fade_in(samples, duration=0.05, sr=22050):
    fade_samples = int(duration * sr)
    fade_samples = min(fade_samples, len(samples))
    result = list(samples)
    for i in range(fade_samples):
        result[i] *= i / fade_samples
    return result


def fade_out(samples, duration=0.05, sr=22050):
    fade_samples = int(duration * sr)
    fade_samples = min(fade_samples, len(samples))
    result = list(samples)
    n = len(result)
    for i in range(fade_samples):
        result[n - 1 - i] *= i / fade_samples
    return result
