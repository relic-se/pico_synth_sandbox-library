# pico_synth_sandbox/audio.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os
from audiomixer import Mixer

class Audio:
    """This class helps manage audio output and mixing.

    :param output: A supported audio output object.
    :type output: object
    :param voice_count: The number of voices to create for the audio mixer. Defaults to 1.
    :type voice_count: int
    :param channel_count: The number of channels needed by the audio output. Defaults to 2 (stereo).
    :type channel_count: int
    :param sample_rate: The sample rate to run the audio output. Defaults to the `AUDIO_RATE` value of `settings.toml` or 22050.
    :type sample_rate: int
    :param buffer_size: The size of the audio buffer in number of samples. Defaults to the `AUDIO_BUFFFER` value of `settings.toml` or 2048.
    :type buffer_size: int
    """

    def __init__(self, output:object, voice_count:int=1, channel_count:int=2, sample_rate:int=None, buffer_size:int=None):
        """Constructor method
        """
        self._output = output
        self.configure(voice_count, channel_count, sample_rate, buffer_size)

    def configure(self, voice_count:int=1, channel_count:int=2, sample_rate:int=None, buffer_size:int=None, bits_per_sample:int=16):
        """Reconfigure the audio mixer using the specified parameters. Will detach and reattach the mixer to the audio output object. Any existing voices will be stopped as well.

        :param voice_count: The number of voices to create for the audio mixer. Defaults to 1.
        :type voice_count: int
        :param channel_count: The number of channels needed by the audio output. Defaults to 2 (stereo).
        :type channel_count: int
        :param sample_rate: The sample rate to run the audio output. Defaults to the `AUDIO_RATE` value of `settings.toml` or 22050.
        :type sample_rate: int
        :param buffer_size: The size of the audio buffer in number of samples. Defaults to the `AUDIO_BUFFFER` value of `settings.toml` or 2048.
        :type buffer_size: int
        """

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

    def set_voice_count(self, value:int):
        """Update the number of voices available on the audio mixer object. Will trigger a reconfiguration of the audio output.

        :param value: The number of voices to create for the audio mixer.
        :type value: int
        """
        self.configure(
            voice_count=value,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample
        )
    def get_voice_count(self) -> int:
        """Get the current number of voices in the audio mixer.
        
        :return: voice count
        :rtype: int
        """
        return len(self._mixer.voice)
    
    def set_channel_count(self, value:int):
        """Update the number of channels in the audio output. Will trigger a reconfiguration of the audio output.

        :param value: The number of channels needed by the audio output.
        :type value: int
        """
        self.configure(
            voice_count=self._voice_count,
            channel_count=value,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample
        )
    def get_channel_count(self) -> int:
        """Get the current number of channels in the audio output.
        
        :return: channel count
        :rtype: int
        """
        return self._channel_count

    def set_sample_rate(self, value:int):
        """Update the sample rate of the audio output. Will trigger a reconfiguration of the audio output.

        :param value: The sample rate to run the audio output.
        :type value: int
        """
        self.configure(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=value,
            buffer_size=self._buffer_size,
            bits_per_sample=self._bits_per_sample
        )
    def get_sample_rate(self) -> int:
        """Get the current sample rate of the audio output.
        
        :return: sample rate in hz
        :rtype: int
        """
        return self._mixer.sample_rate

    def set_buffer_size(self, value:int):
        """Update the size of the audio output buffer. A larger buffer will use more memory and cause more delay between audio updates, but will allow more processing type between updates and generally better audio output stability. Will trigger a reconfiguration of the audio output.

        :param value: The size of the audio buffer in number of samples.
        :type value: int
        """
        self.configure(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=value,
            bits_per_sample=self._bits_per_sample
        )
    def get_buffer_size(self) -> int:
        """Get the current buffer size of teh audio output.
        
        :return: buffer size in samples
        :rtype: int
        """
        return self._buffer_size

    def set_bits_per_sample(self, value:int):
        """Change the bit depth of the audio output. Will trigger a reconfiguration of the audio output.

        :param value: The number of bits per sample. Typically a multiple of 8 such as 8, 16, 24, or 32.
        :type value: int
        """
        self.configure(
            voice_count=self._voice_count,
            channel_count=self._channel_count,
            sample_rate=self._sample_rate,
            buffer_size=self._buffer_size,
            bits_per_sample=value
        )
    def get_bits_per_sample(self) -> int:
        """Get the current number of bits per sample in the audio output.
        
        :return: bits per sample
        :rtype: int
        """
        return self._bits_per_sample

    def set_level(self, value:float, index:int=-1):
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

    def get_level(self, index:int=0) -> float:
        """Gets the current level of a designated voice of the audio mixer. Must be within the range of 0 -> (voice count - 1).
        
        :return: level (0.0 -> 1.0)
        :rtype: float
        """
        return self._mixer.voice[index].level

    def play(self, source:object, index:int=0):
        """Play an audio source through a selected mixer voice.

        :param source: The audio source you would like to play
        :type source: class:`circuitpython_typing.AudioSample`
        :param index: The voice you would like to play the audio source from.
        :type index: int
        """
        if index >= 0 and index < len(self._mixer.voice):
            self._mixer.voice[index].play(source)

    def stop(self, index:int=-1):
        """Stops the designated mixer voice (if valid index is provided) or all currently playing voices of the audio mixer.
        
        :param index: The selected voice index. Must be from 0 -> (voice count - 1). If negative (such as -1), all playing voices will be stopped.
        :type index: int
        """
        if index >= 0 and index < len(self._mixer.voice):
            if self._mixer.voice[index].playing:
                self._mixer.voice[index].stop()
        elif index < 0:
            for voice in self._mixer.voice:
                if voice.playing:
                    voice.stop()
    
    def is_playing(self, index:int=-1) -> bool:
        """Check whether a designated mixer voice is playing (if valid index is provided) or if any voice within the audio mixer is playing.

        :param index: The selected voice index. Must be from 0 -> (voice count - 1). If negative (such as -1), all voices will be checked and will return True if any is playing.
        :type index: int
        :return: voice is playing
        :rtype: bool
        """
        if index >= 0 and index < len(self._mixer.voice):
            return self._mixer.voice[index].playing
        elif index < 0:
            for voice in self._mixer.voice:
                if voice.playing:
                    return True
            return False

    def mute(self):
        """Mute the audio output. Mixer voices will continue playing regardless of muted state.
        """
        self._output.pause()
    def unmute(self):
        """Unmute the audio output to return it to normal operation.
        """
        self._output.resume()
    def is_muted(self) -> bool:
        """Check whether or not the audio output is muted.

        :return: audio mute state
        :rtype: bool
        """
        return self._output.paused
    def toggle_mute(self):
        """Toggle the muted state of the audio output. Mixer voices will continue playing regardless of muted state.
        """
        if self.is_muted():
            self.unmute()
        else:
            self.mute()

class I2SAudio(Audio):
    """This class helps manage audio output and mixing using an :class:`audioio.AudioOut` object of type :class:`audiobusio.I2SOut`.

    :param board: The global board instance.
    :type board: class:`pico_synth_sandbox.board.Board`
    :param voice_count: The number of voices to create for the audio mixer. Defaults to 1.
    :type voice_count: int
    """

    def __init__(self, board:object, voice_count:int=1):
        """Constructor method
        """
        Audio.__init__(self, board.get_i2s_out(), voice_count)

class PWMAudio(Audio):
    """This class helps manage audio output and mixing using an audio output object of type :class:`audiopwmio.PWMAudioOut`.

    :param board: The global board instance.
    :type board: class:`pico_synth_sandbox.board.Board`
    :param voice_count: The number of voices to create for the audio mixer. Defaults to 1.
    :type voice_count: int
    """

    def __init__(self, board:object, voice_count:int=1):
        """Constructor method
        """
        Audio.__init__(self, board.get_pwm_out(), voice_count)

def get_audio_driver(board:object, voice_count:int=1):
    """Automatically generate the proper audio output object based on the board configuration.

    :param board: The global board instance.
    :type board: class:`pico_synth_sandbox.board.Board`
    :param voice_count: The number of voices to create for the audio mixer. Defaults to 1.
    :type voice_count: int
    """
    if board.has_i2s_out():
        return I2SAudio(board, voice_count)
    elif board.has_pwm_out():
        return PWMAudio(board, voice_count)
    else:
        return None
