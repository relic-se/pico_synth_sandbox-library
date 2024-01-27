# pico_synth_sandbox/audio.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os
from audiomixer import Mixer

class Audio:
    """This class helps manage audio output and mixing.

    :param output: An :class:`audioio.AudioOut` object
    :type output: class:`audioio.AudioOut`
    :param voice_count: The number of voices to create for the audio mixer
    :type voice_count: int
    """

    def __init__(self, output, voice_count=1, channel_count=2, sample_rate=None, buffer_size=None):
        """Constructor method
        """
        self._output = output
        self.configure(voice_count, channel_count, sample_rate, buffer_size)

    def configure(self, voice_count=1, channel_count=2, sample_rate=None, buffer_size=None, bits_per_sample=16):
        # Validate parameters
        if voice_count < 1: voice_count = 1
        if channel_count < 1: channel_count = 1
        if sample_rate is None: sample_rate = os.getenv("AUDIO_RATE", 22050)
        if buffer_size is None: buffer_size = os.getenv("AUDIO_BUFFER", 2048)

        # Stop existing objects
        if self._output.playing:
            self._output.stop()
        if hasattr(self, "_mixer") and not self._mixer is None:
            for voice in self._mixer.voice:
                if voice.playing:
                    voice.stop()
            self._mixer = None
        
        # Store parameters
        self._voice_count = voice_count
        self._channel_count = channel_count
        self._sample_rate = sample_rate
        self._buffer_size = buffer_size
        self._bits_per_sample = bits_per_sample
        
        # Create Mixer object and attach to audio output
        self._mixer = Mixer(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample,
            samples_signed=True
        )
        self._output.play(self._mixer)

    def set_voice_count(self, value):
        self.configure(
            voice_count=value,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample
        )
    def get_voice_count(self):
        return len(self._mixer.voice)
    
    def set_channel_count(self, value):
        self.configure(
            voice_count=self._voice_count,
            channel_count=value,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample
        )
    def get_channel_count(self):
        return self._channel_count

    def set_sample_rate(self, value):
        self.configure(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=value,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample
        )
    def get_sample_rate(self):
        return self._mixer.sample_rate

    def set_buffer_size(self, value):
        self.configure(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=value,
            bits_per_sample=self._bits_per_sample
        )
    def get_buffer_size(self):
        return self._buffer_size

    def set_bits_per_sample(self, value):
        self.configure(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=value
        )
    def get_bits_per_sample(self):
        return self._bits_per_sample

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

    def stop(self, index=-1):
        if index >= 0 and index < len(self._mixer.voice):
            if self._mixer.voice[index].playing:
                self._mixer.voice[index].stop()
        elif index < 0:
            for voice in self._mixer.voice:
                if voice.playing:
                    voice.stop()
    
    def is_playing(self, index=-1):
        if index >= 0 and index < len(self._mixer.voice):
            return self._mixer.voice[index].playing
        elif index < 0:
            for voice in self._mixer.voice:
                if voice.playing:
                    return True
            return False

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

class I2SAudio(Audio):
    """This class helps manage audio output and mixing using an :class:`audioio.AudioOut` object of type :class:`audiobusio.I2SOut`.

    :param count: The number of voices to create for the audio mixer
    :type count: int
    """

    def __init__(self, board, voice_count=1):
        """Constructor method
        """
        Audio.__init__(self, board.get_i2s_out(), voice_count)

class PWMAudio(Audio):
    """This class helps manage audio output and mixing using an :class:`audioio.AudioOut` object of type :class:`audiopwmio.PWMAudioOut`.

    :param count: The number of voices to create for the audio mixer
    :type count: int
    """

    def __init__(self, board, voice_count=1):
        """Constructor method
        """
        Audio.__init__(self, board.get_pwm_out(), voice_count)

def get_audio_driver(board, voice_count=1):
    """Automatically generate the proper :class:`audioio.AudioOut` object based on the device's settings.toml configuration.

    :param count: The number of voices to create for the audio mixer, defaults to 1
    :type count: int
    """
    if board.has_i2s_out():
        return I2SAudio(board, voice_count)
    elif board.has_pwm_out():
        return PWMAudio(board, voice_count)
    else:
        return None
