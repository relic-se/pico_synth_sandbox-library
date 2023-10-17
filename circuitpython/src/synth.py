min_filter_frequency = 60.0
max_filter_frequency = min(20000.0, Audio.get_sample_rate() * 0.45)
min_filter_resonance = 0.7071067811865475
max_filter_resonance = 8.0

class Synth:
    NUM_FILTERS = 3
    FILTER_LPF = 0
    FILTER_HPF = 1
    FILTER_BPF = 2

    def __init__(self, audio=None):
        self._synth = synthio.Synthesizer(
            sample_rate=Audio.get_sample_rate(),
            channel_count=2
        )
        if audio is not None: audio.play(self._synth)

        self.voices = []

    def add_voice(self, voice):
        self.voices.append(voice)
        for block in voice.get_blocks():
            self._synth.blocks.append(block)
    def add_voices(self, voices):
        for voice in voices:
            self.add_voice(voice)

    def build_filter(self, type, frequency, resonance):
        if type == Synth.FILTER_LPF:
            return self._synth.low_pass_filter(frequency, resonance)
        elif type == Synth.FILTER_HPF:
            return self._synth.high_pass_filter(frequency, resonance)
        else: #type == Synth.FILTER_BPF:
            return self._synth.band_pass_filter(frequency, resonance)

    def append(self, block):
        self._synth.blocks.append(block)
    def press(self, voice=0, notenum=1, velocity=1.0):
        if isinstance(voice, int) and len(self.voices) > 0:
            voice = self.voices[voice % len(self.voices)]
        if isinstance(voice, synthio.Note):
            self._synth.press(voice)
        elif isinstance(voice, Voice) and voice.press(notenum, velocity):
            self._synth.press(voice.get_notes())
        else:
            return False
        return True
    def release(self, voice=None, force=False):
        if isinstance(voice, int) and len(self.voices) > 0:
            voice = self.voices[voice % len(self.voices)]
        if isinstance(voice, synthio.Note):
            self._synth.release(voice)
        elif isinstance(voice, Voice) and (voice.release() or force):
            self._synth.release(voice.get_notes())
        elif voice is None and len(self.voices) > 0:
            for voice in self.voices:
                self.release(voice)
        else:
            return False
        return True

    def set_waveform(self, waveform):
        for voice in self.voices:
            voice.set_waveform(waveform)

    # Velocity
    def set_velocity_amount(self, value):
        for voice in self.voices:
            voice.set_velocity_amount(value)

    # Filter
    def set_filter_type(self, value, update=True):
        for voice in self.voices:
            voice.set_filter_type(value, self, update)
    def set_filter_frequency(self, value, update=True):
        for voice in self.voices:
            voice.set_filter_frequency(value, self, update)
    def set_filter_resonance(self, value, update=True):
        for voice in self.voices:
            voice.set_filter_resonance(value, self, update)
    def set_filter(self, type=0, frequency=1.0, resonance=0.0, update=True):
        for voice in self.voices:
            voice.set_filter(type, frequency, resonance, self, update)

    @staticmethod
    def calculate_filter_frequency_value(frequency):
        global min_filter_frequency, max_filter_frequency
        return unmap_value(frequency, min_filter_frequency, max_filter_frequency)

    # Loop
    def update(self):
        for voice in self.voices:
            voice.update(self)
