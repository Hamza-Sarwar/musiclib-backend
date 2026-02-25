import random

from . import oscillators, envelopes, effects, theory, drums, mixer, genres


def _get_osc_func(name):
    osc_map = {
        "sine": oscillators.sine_wave,
        "saw": oscillators.saw_wave,
        "square": oscillators.square_wave,
        "triangle": oscillators.triangle_wave,
        "pulse": oscillators.pulse_wave,
    }
    return osc_map.get(name, oscillators.sine_wave)


def _apply_effects_chain(samples, chain, sr=22050):
    for effect_name, *params in chain:
        if effect_name == "low_pass":
            samples = effects.low_pass_filter(samples, cutoff=params[0], sr=sr)
        elif effect_name == "reverb":
            samples = effects.simple_reverb(samples, sr=sr, mix=params[0])
        elif effect_name == "distortion":
            samples = effects.distortion(samples, gain=params[0])
        elif effect_name == "bitcrush":
            samples = effects.bitcrush(samples, bits=params[0])
    return samples


def _render_chords(chord_progression, osc_func, beat_dur, bars, sr, scale_name):
    samples = []
    for _ in range(bars):
        for root_midi, chord_type in chord_progression:
            freqs = theory.get_chord_freqs(root_midi, chord_type)
            note_samples = int(beat_dur * 4 * sr)  # whole note per chord
            chord_buf = [0.0] * note_samples
            for freq in freqs:
                tone = osc_func(freq, beat_dur * 4, sr)
                env = envelopes.adsr_envelope(
                    len(tone), attack=0.02, decay=0.1, sustain=0.6, release=0.1, sr=sr
                )
                for i in range(min(len(tone), note_samples)):
                    chord_buf[i] += tone[i] * env[i] / len(freqs)
            samples.extend(chord_buf)
    return samples


def _render_bass(chord_progression, osc_func, beat_dur, bars, sr):
    samples = []
    for _ in range(bars):
        for root_midi, chord_type in chord_progression:
            bass_midi = root_midi - 12
            freq = theory.midi_to_freq(bass_midi)
            note_dur = beat_dur
            for beat in range(4):
                tone = osc_func(freq, note_dur, sr)
                env = envelopes.adsr_envelope(
                    len(tone), attack=0.01, decay=0.05, sustain=0.7, release=0.05, sr=sr
                )
                tone = envelopes.apply_envelope(tone, env)
                samples.extend(tone)
    return samples


def _render_melody(chord_progression, scale_notes, osc_func, beat_dur, bars, sr, rest_prob):
    all_samples = []
    for _ in range(bars):
        for root_midi, chord_type in chord_progression:
            chord_midis = [root_midi + i for i in theory.CHORD_TYPES.get(chord_type, [0, 4, 7])]
            melody_notes = theory.generate_melody(
                scale_notes, num_beats=4, beat_duration=beat_dur,
                sr=sr, rest_prob=rest_prob, chord_tones_midi=chord_midis,
            )
            for midi_note, dur in melody_notes:
                num_note_samples = int(dur * sr)
                if midi_note == 0:
                    all_samples.extend([0.0] * num_note_samples)
                else:
                    freq = theory.midi_to_freq(midi_note)
                    tone = osc_func(freq, dur, sr)
                    env = envelopes.adsr_envelope(
                        len(tone), attack=0.01, decay=0.05, sustain=0.5, release=0.08, sr=sr
                    )
                    tone = envelopes.apply_envelope(tone, env)
                    all_samples.extend(tone)
    return all_samples


def _render_pad(chord_progression, osc_func, beat_dur, bars, sr):
    samples = []
    for _ in range(bars):
        for root_midi, chord_type in chord_progression:
            freqs = theory.get_chord_freqs(root_midi, chord_type)
            chord_dur = beat_dur * 4
            note_samples = int(chord_dur * sr)
            chord_buf = [0.0] * note_samples
            for freq in freqs:
                tone = osc_func(freq * 2, chord_dur, sr)
                env = envelopes.adsr_envelope(
                    len(tone), attack=0.3, decay=0.2, sustain=0.4, release=0.3, sr=sr
                )
                for i in range(min(len(tone), note_samples)):
                    chord_buf[i] += tone[i] * env[i] / len(freqs)
            samples.extend(chord_buf)
    return samples


def generate_track(genre_name, bpm=None, duration=8, sr=22050):
    template = genres.get_genre_template(genre_name)

    if bpm is None:
        bpm = random.randint(*template["bpm_range"])

    scale_name = random.choice(template["scales"])
    root_midi = random.randint(*template["root_range"])

    genre_key = genre_name.lower().replace("-", "").replace(" ", "")
    prog_options = theory.GENRE_PROGRESSIONS.get(genre_key)
    if not prog_options:
        for alias, target in genres.GENRE_ALIASES.items():
            if alias.replace("-", "").replace(" ", "") == genre_key:
                prog_options = theory.GENRE_PROGRESSIONS.get(target)
                break
    if not prog_options:
        prog_options = theory.GENRE_PROGRESSIONS["electronic"]

    progression_degrees = random.choice(prog_options)
    chord_progression = theory.build_progression(root_midi, scale_name, progression_degrees)

    beat_dur = 60.0 / bpm
    bar_dur = beat_dur * 4 * len(chord_progression)
    bars = max(1, int(duration / bar_dur))
    actual_duration = bars * bar_dur

    target_samples = int(duration * sr)
    scale_notes = theory.get_scale_notes(root_midi, scale_name, octaves=3)
    fx_config = template.get("effects", {})

    def _trim(layer):
        return layer[:target_samples] if len(layer) > target_samples else layer

    # Render layers (trim before effects to avoid processing excess samples)
    chord_osc = _get_osc_func(template["chord_osc"])
    chord_layer = _trim(_render_chords(chord_progression, chord_osc, beat_dur, bars, sr, scale_name))
    chord_layer = _apply_effects_chain(chord_layer, fx_config.get("chords", []), sr)

    bass_osc = _get_osc_func(template["bass_osc"])
    bass_layer = _trim(_render_bass(chord_progression, bass_osc, beat_dur, bars, sr))
    bass_layer = _apply_effects_chain(bass_layer, fx_config.get("bass", []), sr)

    if template["drum_patterns"]:
        drum_layer = drums.sequence_drums(
            template["drum_patterns"], bpm, min(actual_duration, duration), sr,
            swing=template.get("swing", 0.0),
        )
    else:
        drum_layer = [0.0] * target_samples

    melody_osc = _get_osc_func(template["melody_osc"])
    melody_layer = _trim(_render_melody(
        chord_progression, scale_notes, melody_osc, beat_dur, bars, sr,
        rest_prob=template.get("melody_rest_prob", 0.2),
    ))
    melody_layer = _apply_effects_chain(melody_layer, fx_config.get("melody", []), sr)

    pad_osc_name = template.get("pad_osc")
    if pad_osc_name and template["volumes"].get("pad", 0) > 0:
        pad_osc = _get_osc_func(pad_osc_name)
        pad_layer = _trim(_render_pad(chord_progression, pad_osc, beat_dur, bars, sr))
        pad_layer = _apply_effects_chain(pad_layer, fx_config.get("pad", []), sr)
    else:
        pad_layer = [0.0] * target_samples

    # Mix
    vols = template["volumes"]
    layers = [chord_layer, bass_layer, drum_layer, melody_layer, pad_layer]
    volumes = [vols["chords"], vols["bass"], vols["drums"], vols["melody"], vols.get("pad", 0)]

    mixed = mixer.mix_layers(layers, volumes)
    mixed = _apply_effects_chain(mixed, fx_config.get("master", []), sr)

    # Truncate to target duration
    target_samples = int(duration * sr)
    if len(mixed) > target_samples:
        mixed = mixed[:target_samples]

    mixed = mixer.normalize(mixed)
    mixed = envelopes.fade_in(mixed, duration=0.05, sr=sr)
    mixed = envelopes.fade_out(mixed, duration=0.3, sr=sr)

    return mixer.samples_to_wav_bytes(mixed, sr)
