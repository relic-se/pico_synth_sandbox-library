# pico_synth_sandbox/py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import normalize
import os, random, gc
import ulab.numpy as numpy
import adafruit_wave

def get_samples():
    """Retrieve the number of samples in a waveform as defined by `WAVE_SAMPLES` in the settings.toml file.

    :return: waveform buffer size
    :rtype: int
    """
    return os.getenv("WAVE_SAMPLES", 256)

def get_amplitude():
    """Retrieve the maximum level peak-to-peak (+/-) of waveform sample values as defined by `WAVE_AMPLITUDE` in the settings.toml file.

    :return: waveform amplitude level
    :rtype: int
    """
    return os.getenv("WAVE_AMPLITUDE", 12000)

_saw = None
def get_saw():
    """Generate a decrementing sawtooth 

    :return: waveform
    :rtype: numpy array
    """
    global _saw
    if _saw is None:
        _saw = numpy.linspace(get_amplitude(), -get_amplitude(), num=get_samples(), dtype=numpy.int16)
    return _saw

def _get_sine(offset=0.0):
    return numpy.array(numpy.sin(numpy.linspace(offset*numpy.pi, (2+offset)*numpy.pi, get_samples(), endpoint=False)) * get_amplitude(), dtype=numpy.int16)

_sine = None
def get_sine():
    """Generate a sine 

    :return: waveform
    :rtype: numpy array
    """
    global _sine
    if _sine is None:
        _sine = _get_sine()
    return _sine

_offset_sine = None
def get_offset_sine():
    """Generate a sine waveform offset by a quarter period (PI/2).

    :return: waveform
    :rtype: numpy array
    """
    global _offset_sine
    if _offset_sine is None:
        _offset_sine = _get_sine(0.5)
    return _offset_sine

_square = None
def get_square():
    """Generate a square 

    :return: waveform
    :rtype: numpy array
    """
    global _square
    if _square is None:
        _square = numpy.concatenate((numpy.ones(get_samples()//2, dtype=numpy.int16)*get_amplitude(),numpy.ones(get_samples()//2, dtype=numpy.int16)*-get_amplitude()))
    return _square

_triangle = None
def get_triangle():
    """Generate a triangle 

    :return: waveform
    :rtype: numpy array
    """
    global _triangle
    if _triangle is None:
        _triangle = numpy.concatenate((
            numpy.linspace(-get_amplitude(), get_amplitude(), num=get_samples()//2, dtype=numpy.int16),
            numpy.linspace(get_amplitude(), -get_amplitude(), num=get_samples()//2, dtype=numpy.int16)
        ))
    return _triangle

_noise = None
def get_noise():
    """Generate a white (random) noise 

    :return: waveform
    :rtype: numpy array
    """
    global _noise
    if _noise is None:
        _noise = numpy.array([random.randint(-get_amplitude(), get_amplitude()) for i in range(get_samples())], dtype=numpy.int16)
    return _noise

_sine_noise = None
def get_sine_noise():
    """Generate a sine waveform with white noise added. Useful for percussion synthesis.

    :return: waveform
    :rtype: numpy array
    """
    global _sine_noise, _sine, _noise
    if _sine_noise is None:
        get_sine()
        get_noise()
        _sine_noise = numpy.array([int(max(min(_sine[i] + (_noise[i]/2.0), get_amplitude()), -get_amplitude())) for i in range(get_samples())], dtype=numpy.int16)
    return _sine_noise

_offset_sine_noise = None
def get_offset_sine_noise():
    """Generate a sine waveform offset by a quarter period (PI/2) with white noise added. Useful for percussion synthesis.

    :return: waveform
    :rtype: numpy array
    """
    global _offset_sine_noise, _offset_sine, _noise
    if _offset_sine_noise is None:
        get_offset_sine()
        get_noise()
        _offset_sine_noise = numpy.array([int(max(min(_offset_sine[i] + (_noise[i]/2.0), get_amplitude()), -get_amplitude())) for i in range(get_samples())], dtype=numpy.int16)
    return _offset_sine_noise

def load_from_file(filepath, max_samples=4096):
    data = None
    sample_rate = 0

    with adafruit_wave.open(filepath, "rb") as wave:
        if wave.getsampwidth() != 2 or wave.getnchannels() > 2:
            return False
        sample_rate = wave.getframerate()

        # Read sample and convert to numpy
        frames = min(wave.getnframes(), max_samples)
        data = list(memoryview(wave.readframes(frames)).cast('h'))
        if wave.getnchannels() == 2: # Filter out right channel
            data = [i for i in range(0, frames, 2)]
        data = numpy.array(data, dtype=numpy.int16)

        # Normalize volume
        data = normalize(data)

    gc.collect()
    return data, sample_rate
