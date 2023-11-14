# pico_synth_sandbox/audio.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os, board
from audiomixer import Mixer
from audiopwmio import PWMAudioOut
from audiobusio import I2SOut

class Audio:
    """This class helps manage audio output and mixing.

    :param output: An :class:`audioio.AudioOut` object
    :type output: class:`audioio.AudioOut`
    :param count: The number of voices to create for the audio mixer
    :type count: int
    """

    def __init__(self, output, count=1):
        """Constructor method
        """
        if count < 1: count = 1
        self._mixer = Mixer(
            voice_count=count,
            sample_rate=Audio.get_sample_rate(),
            channel_count=2,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=Audio.get_buffer_size()
        )
        self._output = output
        self._output.play(self._mixer)

    def set_level(self, value, index=-1):
        """Set the level of output of all or a single mixer voice.

        :param value: The level of the voice from 0.0 to 1.0
        :type value: float
        :param index: If you are changing the level of a specific mixer voice, provide the index of that voice. If you'd like to change the level of all available voices, leave this parameter unset or provide an integer less than 0.
        :type index: int
        """
        if index < 0:
            for voice in self._mixer.voice:
                voice.level = value
        elif index < len(self._mixer.voice):
            self._mixer.voice[index].level = value

    def play(self, source, index=0):
        """Play an audio source through a selected mixer voice.

        :param source: The audio source you would like to play
        :type source: class:`circuitpython_typing.AudioSample`
        :param index: The voice you would like to play the audio source from.
        :type index: int
        """
        if index >= 0 and index < len(self._mixer.voice):
            self._mixer.voice[index].play(source)

    def mute(self):
        self._output.pause()
    def unmute(self):
        self._output.resume()
    def is_muted(self):
        return self._output.paused
    def toggle_mute(self):
        if self.is_muted():
            self.unmute()
        else:
            self.mute()

    @staticmethod
    def get_sample_rate():
        """Returns the sample rate of the audio mixer as defined by the settings.toml file.

        :return: sample rate
        :rtype: int
        """
        return os.getenv("AUDIO_RATE", 22050)

    @staticmethod
    def get_buffer_size():
        """Returns the buffer size of the audio mixer as defined by the settings.toml file.

        :return: buffer size
        :rtype: int
        """
        return os.getenv("AUDIO_BUFFER", 2048)

class I2SAudio(Audio):
    """This class helps manage audio output and mixing using an :class:`audioio.AudioOut` object of type :class:`audiobusio.I2SOut`.

    :param count: The number of voices to create for the audio mixer
    :type count: int
    """

    def __init__(self, count=1):
        """Constructor method
        """
        Audio.__init__(self, I2SOut(
            bit_clock=board.GP16,
            word_select=board.GP17,
            data=board.GP18
        ), count)

class PWMAudio(Audio):
    """This class helps manage audio output and mixing using an :class:`audioio.AudioOut` object of type :class:`audiopwmio.PWMAudioOut`.

    :param count: The number of voices to create for the audio mixer
    :type count: int
    """

    def __init__(self, count=1):
        """Constructor method
        """
        Audio.__init__(self, PWMAudioOut(
            left_channel=board.GP16,
            right_channel=board.GP17
        ), count)

def get_audio_driver(count=1):
    """Automatically generate the proper :class:`audioio.AudioOut` object based on the device's settings.toml configuration.

    :param count: The number of voices to create for the audio mixer, defaults to 1
    :type count: int
    """
    if os.getenv("AUDIO_DRIVER", "PWM") == "I2S":
        return I2SAudio(count)
    else:
        return PWMAudio(count)

MIN_FILTER_FREQUENCY = 60.0
MAX_FILTER_FREQUENCY = min(20000.0, Audio.get_sample_rate() * 0.45)
MIN_FILTER_RESONANCE = 0.7071067811865475
MAX_FILTER_RESONANCE = 8.0
