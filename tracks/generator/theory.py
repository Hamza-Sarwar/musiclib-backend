import math
import random

SCALES = {
    "major":       [0, 2, 4, 5, 7, 9, 11],
    "minor":       [0, 2, 3, 5, 7, 8, 10],
    "dorian":      [0, 2, 3, 5, 7, 9, 10],
    "mixolydian":  [0, 2, 4, 5, 7, 9, 10],
    "pentatonic":  [0, 2, 4, 7, 9],
    "blues":       [0, 3, 5, 6, 7, 10],
    "whole_tone":  [0, 2, 4, 6, 8, 10],
}

CHORD_TYPES = {
    "major":  [0, 4, 7],
    "minor":  [0, 3, 7],
    "7":      [0, 4, 7, 10],
    "maj7":   [0, 4, 7, 11],
    "min7":   [0, 3, 7, 10],
    "sus2":   [0, 2, 7],
    "sus4":   [0, 5, 7],
    "dim":    [0, 3, 6],
    "aug":    [0, 4, 8],
    "power":  [0, 7],
}


def midi_to_freq(midi_note):
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))


def get_scale_notes(root_midi, scale_name, octaves=2):
    intervals = SCALES.get(scale_name, SCALES["major"])
    notes = []
    for octave in range(octaves):
        for interval in intervals:
            notes.append(root_midi + octave * 12 + interval)
    return notes


def get_chord_freqs(root_midi, chord_type="major"):
    intervals = CHORD_TYPES.get(chord_type, CHORD_TYPES["major"])
    return [midi_to_freq(root_midi + i) for i in intervals]


def build_progression(root_midi, scale_name, progression_degrees):
    scale = SCALES.get(scale_name, SCALES["major"])
    chords = []
    for degree, chord_type in progression_degrees:
        degree_idx = (degree - 1) % len(scale)
        note = root_midi + scale[degree_idx]
        chords.append((note, chord_type))
    return chords


GENRE_PROGRESSIONS = {
    "lofi": [
        [(2, "min7"), (5, "7"), (1, "maj7"), (6, "min7")],
        [(1, "maj7"), (6, "min7"), (4, "maj7"), (5, "7")],
    ],
    "electronic": [
        [(1, "minor"), (6, "major"), (3, "major"), (7, "major")],
        [(1, "minor"), (4, "minor"), (6, "major"), (5, "major")],
    ],
    "ambient": [
        [(1, "maj7"), (4, "maj7"), (1, "maj7"), (5, "sus2")],
        [(1, "major"), (3, "minor"), (4, "major"), (1, "major")],
    ],
    "hiphop": [
        [(1, "minor"), (4, "minor"), (1, "minor"), (5, "minor")],
        [(1, "min7"), (4, "min7"), (6, "major"), (5, "major")],
    ],
    "jazz": [
        [(2, "min7"), (5, "7"), (1, "maj7"), (6, "min7")],
        [(1, "maj7"), (4, "7"), (3, "min7"), (6, "7")],
    ],
    "rock": [
        [(1, "power"), (4, "power"), (5, "power"), (4, "power")],
        [(1, "power"), (3, "power"), (4, "power"), (5, "power")],
    ],
    "acoustic": [
        [(1, "major"), (5, "major"), (6, "minor"), (4, "major")],
        [(1, "major"), (4, "major"), (5, "major"), (1, "major")],
    ],
    "chiptune": [
        [(1, "major"), (4, "major"), (5, "major"), (4, "major")],
        [(1, "minor"), (6, "major"), (3, "major"), (7, "major")],
    ],
}


def generate_melody(scale_notes, num_beats, beat_duration, sr=22050,
                    rest_prob=0.2, chord_tones_midi=None):
    melody_notes = []
    mid = len(scale_notes) // 2
    current_idx = mid

    for beat in range(num_beats):
        if random.random() < rest_prob:
            melody_notes.append((0, beat_duration))
            continue

        if chord_tones_midi and beat % 2 == 0:
            closest_idx = current_idx
            min_dist = 999
            for ct in chord_tones_midi:
                for j, sn in enumerate(scale_notes):
                    if sn == ct and abs(j - current_idx) < min_dist:
                        min_dist = abs(j - current_idx)
                        closest_idx = j
            current_idx = closest_idx
        else:
            step = random.choice([-2, -1, -1, 0, 1, 1, 2])
            current_idx = max(0, min(len(scale_notes) - 1, current_idx + step))

        midi_note = scale_notes[current_idx]
        melody_notes.append((midi_note, beat_duration))

    return melody_notes
