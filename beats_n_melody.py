import logging
from io import BytesIO

import numpy as np
from scipy.io import wavfile
from voxpopuli import Voice, PhonemeList
from voxpopuli.phonemes import Phoneme

from cock_music_smart_music import get_random_progression_freqs
from tools.audio import to_f32_16k, to_wav_bytes, mix_tracks
from tools.melody import get_trinote_progression_freqs
from tools.player import AudioPlayer

TEMPO = 50
BEATS_PER_MEASURE = 4
CHORDS_PROGRESSION = ["Am2", "Dm2", "Am2", "E2"]
LOOPS_COUNT = 40

BEATS_TRACK_FILE = None
BEATS_TRACK_FILE = "tools/data/beats/tight_beat.wav"
BEATS_TRACK_BEAT_COUNT = 16



if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)

    if BEATS_TRACK_FILE is None:
        beat_duration = 60 / TEMPO
    else:
        rate, beats_track = wavfile.read(BEATS_TRACK_FILE)
        beat_duration = len(beats_track) / (rate * BEATS_TRACK_BEAT_COUNT)
        beats_track_looped = np.tile(beats_track,
                                     LOOPS_COUNT * BEATS_PER_MEASURE * len(CHORDS_PROGRESSION) // BEATS_TRACK_BEAT_COUNT)

    logging.info("Beat time : %dms" % (beat_duration * 1000))
    logging.info("Measure time : %dms" % (beat_duration * 1000 * 4))

    # prog_freqs = get_trinote_progression_freqs(CHORDS_PROGRESSION, BEATS_PER_MEASURE)
    # logging.info("First freq progression: \n %s" % (str(prog_freqs)))
    track_freqs = []
    for _ in range(LOOPS_COUNT):
        track_freqs += get_trinote_progression_freqs(CHORDS_PROGRESSION, BEATS_PER_MEASURE)
        # track_freqs += get_random_progression_freqs(CHORDS_PROGRESSION)

    progression_phonems = PhonemeList([])
    for freq in track_freqs:
        progression_phonems.append(
            Phoneme("o", int(beat_duration * 1000), [(0,freq), (100,freq)])
        )
    logging.info("Rendering audio")

    voice = Voice(lang="fr", voice_id=4)
    wav = voice.to_audio(progression_phonems)
    if BEATS_TRACK_FILE is not None:
        rate, wave_array = to_f32_16k(wav)
        mixed_tracks = mix_tracks(beats_track_looped * 0.5, wave_array * 0.7, align="left")
        wav = to_wav_bytes(mixed_tracks, 16000)
    player = AudioPlayer()
    with open("/tmp/gros_beat.wav", "wb") as wavfile:
        wavfile.write(wav)
    player.set_file(BytesIO(wav))
    player.play()
    player.close()