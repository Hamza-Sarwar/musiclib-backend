import io
import struct
import wave


def mix_layers(layers, volumes=None):
    if not layers:
        return []
    max_len = max(len(layer) for layer in layers)
    if volumes is None:
        volumes = [1.0] * len(layers)
    mixed = [0.0] * max_len
    for layer, vol in zip(layers, volumes):
        for i in range(len(layer)):
            mixed[i] += layer[i] * vol
    return mixed


def normalize(samples, target_peak=0.85):
    if not samples:
        return samples
    peak = max(abs(s) for s in samples)
    if peak == 0:
        return samples
    scale = target_peak / peak
    return [s * scale for s in samples]


def samples_to_wav_bytes(samples, sr=22050):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        max_val = 32767
        frame_data = b"".join(
            struct.pack("<h", max(-max_val, min(max_val, int(s * max_val))))
            for s in samples
        )
        wf.writeframes(frame_data)
    buf.seek(0)
    return buf.read()
