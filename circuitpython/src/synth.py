class Synth:
    NUM_FILTERS = 3
    FILTER_LPF = 0
    FILTER_HPF = 1
    FILTER_BPF = 2

    def __init__(self, audio=None, voices=12, root=440.0):
        self._synth = synthio.Synthesizer(
            sample_rate=audio.get_sample_rate() if audio is not None else 22050,
            channel_count=2
        )
        if audio is not None: audio.play(self._synth)

        self.voices = [Voice(self, root) for i in range(voices)]

    def build_filter(self, type, frequency, resonance):
        if type == Synth.FILTER_LPF:
            return self._synth.low_pass_filter(frequency, resonance)
        elif type == Synth.FILTER_HPF:
            return self._synth.high_pass_filter(frequency, resonance)
        else: #type == Synth.FILTER_BPF:
            return self._synth.band_pass_filter(frequency, resonance)

    def append(self, block):
        self._synth.blocks.append(block)
    def press(self, note = None):
        if isinstance(note, synthio.Note):
            self._synth.press(note)
        elif isinstance(note, Voice):
            self._synth.press(note.get())
        elif isinstance(note, int):
            self.voices[0].press(note)
        else:
            return False
        return True
    def release(self, note = None):
        if isinstance(note, synthio.Note):
            self._synth.release(note)
        elif isinstance(note, Voice):
            self._synth.release(note.get())
        elif isinstance(note, int):
            self.voices[note % len(self.voices)].release()
        elif note is None:
            for i in range(12):
                self.voices[i].release()
        else:
            return False
        return True

    def set_waveform(self, waveform):
        for voice in self.voices:
            voice.set_waveform(waveform)

    # Envelope
    def set_velocity_amount(self, value):
        for voice in self.voices:
            voice.set_velocity_amount(value)
    def set_envelope_attack_time(self, value, update=True):
        for voice in self.voices:
            voice.set_envelope_attack_time(value, update)
    def set_envelope_decay_time(self, value, update=True):
        for voice in self.voices:
            voice.set_envelope_decay_time(value, update)
    def set_envelope_release_time(self, value, update=True):
        for voice in self.voices:
            voice.set_envelope_release_time(value, update)
    def set_envelope_attack_level(self, value, update=True):
        for voice in self.voices:
            voice.set_envelope_attack_level(value, update)
    def set_envelope_sustain_level(self, value, update=True):
        for voice in self.voices:
            voice.set_envelope_sustain_level(value, update)
    def set_envelope(self, velocity_amount=1.0, attack_time=0.0, decay_time=0.0, release_time=0.0, attack_level=1.0, sustain_level=0.75, update=True):
        for voice in self.voices:
            voice.set_envelope(velocity_amount, attack_time, decay_time, release_time, attack_level, sustain_level, update)

    # Filter
    def set_filter_type(self, value, update=True):
        for voice in self.voices:
            voice.set_filter_type(value, update)
    def set_filter_frequency(self, value, update=True):
        for voice in self.voices:
            voice.set_filter_frequency(value, update)
    def set_filter_resonance(self, value, update=True):
        for voice in self.voices:
            voice.set_filter_resonance(value, update)
    def set_filter_envelope_attack_time(self, value):
        for voice in self.voices:
            voice.set_filter_envelope_attack_time(value)
    def set_filter_envelope_release_time(self, value):
        for voice in self.voices:
            voice.set_filter_envelope_release_time(value)
    def set_filter_envelope_amount(self, value):
        for voice in self.voices:
            voice.set_filter_envelope_amount(value)
    def set_filter_lfo_rate(self, value):
        for voice in self.voices:
            voice.set_filter_lfo_rate(value)
    def set_filter_lfo_depth(self, value):
        for voice in self.voices:
            voice.set_filter_lfo_depth(value)
    def set_filter(self, type=0, frequency=1.0, resonance=0.0, envelope_attack_time=0.0, envelope_release_time=0.0, envelope_amount=0.0, lfo_rate=1.0, lfo_depth=0.0, update=True):
        for voice in self.voices:
            voice.set_filter(type, frequency, resonance, envelope_attack_time, envelope_release_time, envelope_amount, lfo_rate, lfo_depth, update)

    # Loop
    def update(self):
        for voice in self.voices:
            voice.update()

    def get_sample_rate(self):
        return self._synth.sample_rate
