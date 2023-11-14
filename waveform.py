# pico_synth_sandbox/waveform.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import clamp
import os, random, gc
import ulab.numpy as numpy
import adafruit_wave

class Waveform:
    """A static helper class to quickly generate waveforms. Stores generated waveform arrays locally to improve memory efficiency.
    """

    @staticmethod
    def get_samples():
        """Retrieve the number of samples in a waveform as defined by `WAVE_SAMPLES` in the settings.toml file.

        :return: waveform buffer size
        :rtype: int
        """
        return os.getenv("WAVE_SAMPLES", 256)

    @staticmethod
    def get_amplitude():
        """Retrieve the maximum level peak-to-peak (+/-) of waveform sample values as defined by `WAVE_AMPLITUDE` in the settings.toml file.

        :return: waveform amplitude level
        :rtype: int
        """
        return os.getenv("WAVE_AMPLITUDE", 12000)

    @staticmethod
    def get_saw():
        """Generate a decrementing sawtooth waveform.

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_saw"):
            Waveform._saw = numpy.linspace(Waveform.get_amplitude(), -Waveform.get_amplitude(), num=Waveform.get_samples(), dtype=numpy.int16)
        return Waveform._saw

    @staticmethod
    def _get_sine(offset=0.0):
        return numpy.array(numpy.sin(numpy.linspace(offset*numpy.pi, (2+offset)*numpy.pi, Waveform.get_samples(), endpoint=False)) * Waveform.get_amplitude(), dtype=numpy.int16)

    @staticmethod
    def get_sine():
        """Generate a sine waveform.

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_sine"):
            Waveform._sine = Waveform._get_sine()
        return Waveform._sine

    @staticmethod
    def get_offset_sine():
        """Generate a sine waveform offset by a quarter period (PI/2).

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_offset_sine"):
            Waveform._offset_sine = Waveform._get_sine(0.5)
        return Waveform._offset_sine

    @staticmethod
    def get_square():
        """Generate a square waveform.

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_square"):
            Waveform._square = numpy.concatenate((numpy.ones(Waveform.get_samples()//2, dtype=numpy.int16)*Waveform.get_amplitude(),numpy.ones(Waveform.get_samples()//2, dtype=numpy.int16)*-Waveform.get_amplitude()))
        return Waveform._square

    @staticmethod
    def get_noise():
        """Generate a white (random) noise waveform.

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_noise"):
            Waveform._noise = numpy.array([random.randint(-Waveform.get_amplitude(), Waveform.get_amplitude()) for i in range(Waveform.get_samples())], dtype=numpy.int16)
        return Waveform._noise

    @staticmethod
    def get_sine_noise():
        """Generate a sine waveform with white noise added. Useful for percussion synthesis.

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_sine_noise"):
            Waveform.get_sine()
            Waveform.get_noise()
            Waveform._sine_noise = numpy.array([int(max(min(Waveform._sine[i] + (Waveform._noise[i]/2.0), Waveform.get_amplitude()), -Waveform.get_amplitude())) for i in range(Waveform.get_samples())], dtype=numpy.int16)
        return Waveform._sine_noise

    @staticmethod
    def get_offset_sine_noise():
        """Generate a sine waveform offset by a quarter period (PI/2) with white noise added. Useful for percussion synthesis.

        :return: waveform
        :rtype: numpy array
        """
        if not hasattr(Waveform, "_offset_sine_noise"):
            Waveform.get_offset_sine()
            Waveform.get_noise()
            Waveform._offset_sine_noise = numpy.array([int(max(min(Waveform._offset_sine[i] + (Waveform._noise[i]/2.0), Waveform.get_amplitude()), -Waveform.get_amplitude())) for i in range(Waveform.get_samples())], dtype=numpy.int16)
        return Waveform._offset_sine_noise

    @staticmethod
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
            max_level = numpy.max(data)
            if max_level < 32767.0:
                for i in range(len(data)):
                    data[i] = int(clamp(float(data[i]) * 32767.0 / max_level, -32767.0, 32767.0))

        gc.collect()
        return data, sample_rate
