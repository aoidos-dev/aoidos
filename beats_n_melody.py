from typing import List
import json
from os import path
import logging
import numpy as np
from io import BytesIO
from scipy.io import wavfile

from voxpopuli import Voice, PhonemeList
from voxpopuli.phonemes import Frenchphonemes, Phoneme

from tools.audio import to_f32_16k, to_wav_bytes, mix_tracks
from tools.melody import get_harmonies
from tools.player import AudioPlayer

TEMPO = 100
BEATS_PER_MEASURE = 4
CHORDS_PROGRESSION = ["Am4", "Am4", "F4", "Em4"]
LOOPS_COUNT = 10

BEATS_TRACK_FILE = None
BEATS_TRACK_FILE = "tools/data/beats/sample_3.wav"
BEATS_TRACK_BEAT_COUNT = 4

pitch_filepath = path.join(path.dirname(path.realpath(__file__)), "tools/data/pitches.json")
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

def get_progression_freqs(progression : List[str]) -> List[float]:
    track_frequencies = []
    blinker = False
    for chord in progression:
        chords_freqs = get_chord_harmonies(chord)
        for i in range(BEATS_PER_MEASURE):
            track_frequencies.append(chords_freqs[1] if blinker else chords_freqs[0])
            blinker = not blinker
    return track_frequencies

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    if BEATS_TRACK_FILE is None:
        beat_duration = 60 / TEMPO
    else:
        rate, beats_track = wavfile.read(BEATS_TRACK_FILE)
        beat_duration = len(beats_track) / (rate * BEATS_TRACK_BEAT_COUNT)
        beats_track_looped = np.tile(beats_track, LOOPS_COUNT * BEATS_TRACK_BEAT_COUNT)

    logging.info("Beat time : %dms" % (beat_duration * 1000))
    logging.info("Measure time : %dms" % (beat_duration * 1000 * 4))

    prog_freqs = get_progression_freqs(CHORDS_PROGRESSION)
    logging.info("First freq progression: \n %s" % (str(prog_freqs)))
    track_freqs = prog_freqs * LOOPS_COUNT

    progression_phonems = PhonemeList([])
    for freq in track_freqs:
        progression_phonems.append(
            Phoneme("a", int(beat_duration * 1000), [(0,freq), (100,freq)])
        )
    logging.info("Rendering audio")

    voice = Voice(lang="fr", voice_id=3)
    wav = voice.to_audio(progression_phonems)
    if BEATS_TRACK_FILE is not None:
        rate, wave_array = to_f32_16k(wav)
        mixed_tracks = mix_tracks(beats_track_looped * 0.6, wave_array * 0.4, align="left")
        wav = to_wav_bytes(mixed_tracks, 16000)
    player = AudioPlayer()
    player.set_file(BytesIO(wav))
    player.play()
    player.close()