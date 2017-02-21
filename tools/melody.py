
"""Tools for melodies used in phonems"""
from typing import List
import random
from os import path
import json

au_clair_de_la_lune = ["C4"] * 3 + ["D4", "E4", "C4", "D4", "E4", "D4"]

chord_progressions =[
    ["C", "Am", "F", "G"],
    ["D", "Bm", "G", "A"],
    ["G", "Em", "C", "D"],
    ["C", "Am", "D", "G"],
    ["D", "Bm", "Em", "A"],
    ["G", "Em", "Am", "D"],
    ["C", "Em", "F", "G"],
    ["G", "Bm", "C", "D"],
    ["C", "F", "C", "G"],
    ["A", "D", "A", "E"],
]

chords_ratios = {
    "major" : [0, 3, 6],
    "minor" : [0, 2, 6],
}


def get_freqs(fundamental : int, ratios : List[int]):
    return [int(round(fundamental * (1 + r/12))) for r in ratios]


def get_harmonies(note_pitch, chord_type="major") -> List[int]:
    return get_freqs(note_pitch, chords_ratios[chord_type])

pitch_filepath = path.join(path.dirname(path.realpath(__file__)), "data/pitches.json")
with open(pitch_filepath) as pitch_file:
    pitches = json.load(pitch_file)

def get_chord_harmonies(chord_str : str) -> List[int]:
    octave = int(chord_str[-1])
    chord = chord_str[:-1]
    if chord.endswith("m"):
        note, chord_type = chord.strip("m"), "minor"
    else:
        note, chord_type = chord, "major"
    return get_harmonies(pitches[note + str(octave)], chord_type)

def get_progression_freqs(progression : List[str], beats_per_measure) -> List[float]:
    track_frequencies = []
    blinker = False
    for chord in progression:
        chords_freqs = get_chord_harmonies(chord)
        for i in range(beats_per_measure):
            track_frequencies.append(chords_freqs[2] if blinker else chords_freqs[0])
            blinker = not blinker
    return track_frequencies

def get_trinote_progression_freqs(progression : List[str], beats_per_measure) -> List[float]:
    track_frequencies = []
    freqs_index = [0, 2, 0, 1]
    for chord in progression:
        chords_freqs = get_chord_harmonies(chord)
        for i in range(beats_per_measure):
            track_frequencies.append(chords_freqs[freqs_index[i]])
    return track_frequencies

def get_random_progression_freqs(progression : List[str], beats_per_measure) -> List[float]:
    track_frequencies = []
    freqs_index = [0, 2, 0, 1]
    for chord in progression:
        chords_freqs = get_chord_harmonies(chord)
        for i in range(beats_per_measure):
            track_frequencies.append(chords_freqs[random.choice(freqs_index)])
    return track_frequencies


class AudioTrack:
    pass


class MelodicSynthTrack(AudioTrack):

    def __init__(self, beats_per_measures, chords_progression):
        pass


class RawAudioSynthTrack(AudioTrack):

    def __init__(self, audio_file):
        pass
