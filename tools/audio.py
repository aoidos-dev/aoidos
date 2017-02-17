from subprocess import PIPE, run
from io import BytesIO
import numpy as np
from scipy.io import wavfile

def resample(wave_data : np.ndarray, sample_in, sample_out=16000):
    """Uses sox to resample the wave data array"""
    cmd = "sox -N -V1 -t f32 -r %s -c 1 - -t f32 -r %s -c 1 -" % (sample_in, sample_out)
    output = run(cmd, shell=True, stdout=PIPE, stderr=PIPE, input=wave_data.tobytes(order="f")).stdout
    return np.fromstring(output, dtype=np.float32)

def to_wav_bytes(data: np.ndarray, rate: int) -> bytes:
    # casting it back to int16
    data = (data * (2. ** 15)).astype("int16")
    # then, converting it back to binary data
    bytes_obj = bytes()
    bytes_buff = BytesIO(bytes_obj)
    wavfile.write(bytes_buff, rate, data)
    return bytes_buff.read()

def to_f32_16k(wav: bytes) -> np.ndarray:
    # converting the wav to ndarray, which is much easier to use for DSP
    rate, data = wavfile.read(BytesIO(wav))
    # casting the data array to the right format (float32, for usage by pysndfx)
    data = (data / (2. ** 15)).astype('float32')
    if rate != 16000:
        data = resample(data, rate)
        rate = 16000

    return rate, data

def mix_tracks(track1, track2, offset=None, align=None):
    """Function that mixes two tracks of unequal lengths(represented by numpy arrays) together,
    using an 'align' or an offset. Zero padding is added to the smallest track as to make it fit.

    if offset is defined:
    longest track :  [=============================]
    smallest track : [0000000][================][00]
                      offset
    or
    longest track :  [=============================][00]
    smallest track : [000000000000000][================]
                          offset

    if align is defined:
    left:
    longest track :  [=============================]
    smallest track : [=====================][000000]

    right:
    longest track :  [=============================]
    smallest track : [000000][=====================]

    center:
    longest track :  [=============================]
    smallest track : [000][===================][000]
    """
    short_t, long_t = (track1, track2) if len(track1) < len(track2) else (track2, track1)
    diff = len(long_t) - len(short_t)

    if offset is not None:
        if len(long_t) - (len(short_t) + offset) >= 0:
            padded_short_t = np.pad(short_t, (offset, diff - offset), "constant", constant_values=0.0)
        else: # if offset + short > long, we have to padd the end of the long one
            padded_short_t = np.pad(short_t, (offset, 0), "constant", constant_values=0.0)
            long_t = np.pad(long_t, (0, offset - diff), "constant", constant_values=0.0)

    elif align is not None and align in ["left", "right", "center"]:
        if align == "right":
            padded_short_t = np.pad(short_t, (diff, 0), "constant", constant_values=0.0)
        elif align == "left":
            padded_short_t = np.pad(short_t, (0, diff), "constant", constant_values=0.0)
        elif align == "center":
            left = diff // 2
            right = left if diff % 2 == 0 else left + 1
            padded_short_t = np.pad(short_t, (left, right), "constant", constant_values=0.0)
    else:
        raise Exception()

    # the result vector's elements are c_i = a_i + b_i
    return padded_short_t + long_t