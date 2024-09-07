# pico_synth_sandbox/voice/sample.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os
from pico_synth_sandbox import fftfreq, LOG_2
from pico_synth_sandbox.voice import Voice
from pico_synth_sandbox.voice.oscillator import Oscillator
import pico_synth_sandbox.waveform as waveform
import math, time

class Sample(Oscillator):
    """Create a synthesizer voice from a provided audio sample. Handles pitch, looping points, and wav file loading and inherits all properties and functionality of the :class:`pico_synth_sandbox.voice.oscillator.Oscillator`.

    :param loop: Whether or not to continuously loop the sample or play it once when the voice is pressed. Defaults to true.
    :type loop: bool
    :param filepath: The absolute path to the compatible audio file (`.wav`). Leave empty to initialize the voice without a specified sample. Defaults to empty.
    :type filepath: str
    """

    def __init__(self, loop:bool=True, filepath:str=""):
        """Constructor method
        """
        Oscillator.__init__(self)

        self._loop = loop

        # TODO: Obtain sample rate from synth object (synth.get_sample_rate)?
        self._sample_rate = os.getenv("AUDIO_RATE", 22050)
        self._wave_rate = self._sample_rate
        self._sample_tune = 0.0
        self._loop_tune = 0.0
        self._start = None
        self._desired_frequency = self._root

        if filepath:
            self.load_from_file(filepath)

    def load(self, data, sample_rate:int, root:float=None):
        """Load waveform data from a sample and calculate root frequency, tuning, duration, and other necessary properties.

        :param data: A `ulab.numpy.int16` array to be used as the audio sample data.
        :type data: :class:`ulab.numpy.ndarray`
        :param sample_rate: The recorded audio sample rate of the incoming sample data.
        :type sample_rate: int
        :param root: The predesignated root frequency (in hertz) of the recorded audio sample. Used to match pitch frequencies with pressed notes. If left as `None`, the root frequency will be automatically calculated using the included Fast-Fourier Transform tool, `pico_synth_sandbox.fftfreq`. Defaults to `None`.
        :type root: float
        """
        self._wave_rate = sample_rate
        self.set_waveform(data)
        if root is None:
            self._root = fftfreq(
                data=self._note.waveform,
                sample_rate=self._wave_rate
            )
        self._wave_duration = 1.0 / self._root
        self._sample_duration = len(self._note.waveform) / self._wave_rate
        self._sample_tune = math.log(self._wave_duration / self._sample_duration) / LOG_2
        self.set_loop() # calls self._update_root

    def load_from_file(self, filepath:str, max_samples:int=4096):
        """Load waveform data from an audio `.wav` file within the virtual file system. The audio sample rate and root frequency will be automatically calculated by the file properties and FFT algorithm.

        :param filepath: The absolute path to the `.wav` file.
        :type filepath: str
        :param max_samples: The maximum limit of which to load audio samples from the audio file. Used to avoid memory overflow with large audio files. Defaults to 4096 samples.
        :type max_samples: int
        """
        data, sample_rate = waveform.load_from_file(filepath, max_samples)
        self.load(data, sample_rate)

    def unload(self):
        """Remove sample data from the voice to restore it to its initial state. Will prevent the voice from responding to note presses.
        """
        self._wave_rate = self._sample_rate
        self.set_waveform(None)
        self._root = self._desired_frequency
        self._wave_duration = 1.0 / self._root
        self._sample_duration = 0.0
        self._sample_tune = 0.0
        self._update_root()

    def press(self, notenum:int, velocity:float) -> bool:
        if self._note.waveform is None:
            return False
        if not Oscillator.press(self, notenum, velocity):
            return False
        if not self._loop:
            self._start = time.monotonic()
        return True

    def get_duration(self) -> float:
        """Calculates the length of the audio sample given the current state (includes note bend properties). Used for determining when to release a note during single-shot sample playback.

        :return: The length of the sample playback in seconds.
        :rtype: float
        """
        return self._sample_duration * self._root / pow(2,self._note.bend.value) / self._desired_frequency

    def set_loop(self, start:float=0.0, end:float=1.0):
        """Set the looping parameters of the sample data. Both start and end parameters are relative to the beginning and end of sample data (0.0 - 1.0). Loop points must be at least greater than 2 samples of each other to properly adjust sample tuning.

        :param start: The starting loop point relative to the sample data length. Must be less than `end`. Defaults to 0.0.
        :type start: float
        :param end: The ending loop point relative to the sample data length. Must be greater than `start`. Defaults to 1.0.
        :type end: float
        """
        Oscillator.set_loop(self, start, end)

        length = self._note.waveform_loop_end - self._note.waveform_loop_start
        if length < 2:
            return

        sample_length = len(self._note.waveform)
        self._loop_tune = math.log(sample_length / length) / LOG_2 if length != sample_length else 0.0
        self._update_root()

    def _update_root(self):
        Oscillator._update_root(self)
        self._note.frequency = self._note.frequency * pow(2,self._sample_tune) * pow(2,self._loop_tune)

    async def update(self, synth):
        await Voice.update(self, synth)
        if not self._loop and not self._start is None and time.monotonic() - self._start >= self.get_duration():
            synth.release(self)
            self._start = None
