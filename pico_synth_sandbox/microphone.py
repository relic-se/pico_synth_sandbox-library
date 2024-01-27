# pico_synth_sandbox/microphone.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import resample
import os
import adafruit_wave
import array
import ulab.numpy as numpy

class Microphone:

    def __init__(self, board, sample_rate=None):

        # Settings
        self.desired_sample_rate = sample_rate if not sample_rate is None else Microphone.get_sample_rate()
        self.actual_sample_rate = self.desired_sample_rate * 2 # For some reason, writer doubles the pitch. Double the sample rate to fix this.
        self.input_sample_rate = max(self.actual_sample_rate, 16000)

        self.level_samples = 32

        # Input & Buffer
        self.input = board.get_pdm(self.input_sample_rate)
        self._buffer_raw = None
        self._buffer_data = None
        self._data = None

        # Callbacks
        self._trigger = None

    def get_buffer(self, samples):
        if self._buffer_raw is None or len(self._buffer_data) != samples:
            del self._buffer_raw, self._buffer_data
            self._buffer_raw = array.array('H', [0] * samples)
            self._buffer_data = numpy.frombuffer(self._buffer_raw, dtype=numpy.uint16)
        self.input.record(self._buffer_raw, samples)
        return self._buffer_data

    def get_data(self, samples):
        del self._data
        self.get_buffer(samples)
        mean = numpy.mean(self._buffer_data)
        self._data = numpy.array(resample(self._buffer_data, self.input_sample_rate, self.actual_sample_rate) - mean, dtype=numpy.int16)
        return self._data

    def calculate_level(self, data):
        return numpy.sum(abs(data)) / len(data) / 32768.0
    def get_level(self, samples=None):
        if samples is None: samples = self.level_samples
        return self.calculate_level(self.get_data(samples))

    def calculate_smooth_level(self, level, current=0.0, speed=0.1, samples=None):
        if samples is None: samples = self.level_samples
        rate = min(samples / (self.actual_sample_rate * speed), 1.0) if speed > 0.0 else 1.0
        return current * (1.0 - rate) + level * rate
    def get_smooth_level(self, current=0.0, speed=0.1, samples=None):
        return self.calculate_smooth_level(self.get_level(samples), current, speed, samples)

    def read(self, samples, trigger=0.0, clip=0.0):
        if samples < self.level_samples:
            return False

        if trigger > 0.0:
            data = numpy.zeros(samples, dtype=numpy.int16)

            # Wait for trigger
            while True:
                data[:self.level_samples] = self.get_data(self.level_samples)
                if self.calculate_level(data[:self.level_samples]) >= trigger:
                    break
            if self._trigger: self._trigger()

            # Record remaining samples
            data[self.level_samples:] = self.get_data(samples-self.level_samples)
        else:
            data = self.get_data(samples)

        # Clip tail if below level
        if clip > 0.0:
            for i in range(0, samples, self.level_samples):
                if self.calculate_level(data[i:i+self.level_samples]) < clip:
                    data = data[:i]
                    break

        return data

    def record(self, name, samples, trigger=None, clip=True):
        # Read microphone input
        data = self.read(samples, trigger, clip)
        if not data:
            return False

        # Remove existing file
        filepath = "/samples/{}.wav".format(name)
        try:
            os.remove(filepath)
        except:
            pass

        # Write to file
        writer = adafruit_wave.open(filepath, mode="wb")
        writer.setframerate(self.desired_sample_rate)
        writer.setnchannels(1)
        writer.setsampwidth(2)
        writer.writeframes(array.array('h', data))

        return filepath

    def set_trigger(self, callback):
        self._trigger = callback

    @staticmethod
    def get_sample_rate():
        return os.getenv("MIC_RATE", 11025)
