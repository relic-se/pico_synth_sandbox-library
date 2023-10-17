log2 = math.log(2) # for octave conversion

class Oscillator(Voice):
    def __init__(self, root=440.0):
        Voice.__init__(self)

        self._filter_envelope = AREnvelope()
        self._filter_lfo = synthio.LFO(
            waveform=None,
            rate=1.0,
            scale=0.0,
            offset=0.0
        )

        self._root = root
        self.coarse_tune = 0.0
        self.fine_tune = 0.0
        self.bend_amount = 0.0
        self.bend = 0.0

        self._attack_time = 0.0
        self._decay_time = 0.0
        self._release_time = 0.0
        self._attack_level = 1.0
        self._sustain_level = 0.75

        self._freq_lerp = LerpBlockInput()
        self._pitch_lerp = LerpBlockInput()
        self._note = synthio.Note(
            waveform=None,
            frequency=self._root,
            amplitude=synthio.LFO( # Tremolo
                waveform=None,
                rate=1.0,
                scale=0.0,
                offset=1.0
            ),
            bend=synthio.Math(
                synthio.MathOperation.SUM,
                self._freq_lerp.get(), # Frequency Lerp
                synthio.LFO( # Vibrato
                    waveform=None,
                    rate=1.0,
                    scale=0.0,
                    offset=0.0
                ),
                self._pitch_lerp.get() # Pitch Bend Lerp
            ),
            panning=synthio.LFO(
                waveform=None,
                rate=1.0,
                scale=0.0,
                offset=0.0
            )
        )

    def get_notes(self):
        return [self._note]
    def get_blocks(self):
        return self._filter_envelope.get_blocks() + self._freq_lerp.get_blocks() + self._pitch_lerp.get_blocks() + [
            self._filter_lfo,
            self._note.amplitude,
            self._note.bend,
            self._note.panning,
        ]

    def press(self, notenum, velocity=1.0):
        if not Voice.press(self, notenum, velocity):
            return False
        frequency = synthio.midi_to_hz(notenum)
        self.set_frequency(frequency)
        self._filter_envelope.press()
        return True
    def release(self):
        if not Voice.release(self):
            return False
        self._filter_envelope.release()
        return True

    def set_frequency(self, value):
        global log2
        self._freq_lerp.set(math.log(value/self._root)/log2)
    def set_glide(self, value):
        self._freq_lerp.set_rate(value)

    def set_pitch_bend_amount(self, value):
        self.bend_amount = value
        self._update_pitch_bend()
    def set_pitch_bend(self, value):
        self.bend = value
        self._update_pitch_bend()
    def _update_pitch_bend(self):
        self._pitch_lerp.set(self.bend * self.bend_amount)

    def set_coarse_tune(self, value):
        self.coarse_tune = value
        self._update_root()
    def set_fine_tune(self, value):
        self.fine_tune = value
        self._update_root()
    def _update_root(self):
        self._note.frequency = self._root * pow(2,self.coarse_tune) * pow(2,self.fine_tune)

    def set_waveform(self, waveform):
        self._note.waveform = waveform

    def set_level(self, value):
        self._note.amplitude.offset = value
    def set_tremolo_rate(self, value):
        self._note.amplitude.rate = value
    def set_tremolo_depth(self, value):
        self._note.amplitude.scale = value

    def set_vibrato_rate(self, value):
        self._note.bend.b.rate = value
    def set_vibrato_depth(self, value):
        self._note.bend.b.scale = value

    def set_pan_rate(self, value):
        self._note.panning.rate = value
    def set_pan_depth(self, value):
        self._note.panning.scale = value
    def set_pan(self, value):
        self._note.panning.offset = value

    # Envelope
    def _update_envelope(self):
        mod = self._get_velocity_mod()
        self._note.envelope = synthio.Envelope(
            attack_time=self._attack_time,
            decay_time=self._decay_time,
            release_time=self._release_time,
            attack_level=mod*self._attack_level,
            sustain_level=mod*self._sustain_level
        )
    def set_envelope_attack_time(self, value, update=True):
        self._attack_time = value
        if update: self._update_envelope()
    def set_envelope_decay_time(self, value, update=True):
        self._decay_time = value
        if update: self._update_envelope()
    def set_envelope_release_time(self, value, update=True):
        self._release_time = value
        if update: self._update_envelope()
    def set_envelope_attack_level(self, value, update=True):
        self._attack_level = value
        if update: self._update_envelope()
    def set_envelope_sustain_level(self, value, update=True):
        self._sustain_level = value
        if update: self._update_envelope()
    def set_envelope(self, velocity_amount=1.0, attack_time=0.0, decay_time=0.0, release_time=0.0, attack_level=1.0, sustain_level=0.75, update=True):
        self.set_velocity_amount(velocity_amount)
        self.set_envelope_attack_time(attack_time, False)
        self.set_envelope_decay_time(decay_time, False)
        self.set_envelope_release_time(release_time, False)
        self.set_envelope_attack_level(attack_level, False)
        self.set_envelope_sustain_level(sustain_level, False)
        if update: self._update_envelope()

    # Filter
    def _get_filter_frequency_value(self):
        return self._filter_frequency + self._filter_envelope.get_value() + self._filter_lfo.value
    def set_filter_envelope_attack_time(self, value):
        self._filter_envelope.set_attack(value)
    def set_filter_envelope_release_time(self, value):
        self._filter_envelope.set_release(value)
    def set_filter_envelope_amount(self, value):
        self._filter_envelope.set_amount(value)
    def set_filter_lfo_rate(self, value):
        self._filter_lfo.rate = value
    def set_filter_lfo_depth(self, value):
        self._filter_lfo.scale = value
    def set_filter(self, type=0, frequency=1.0, resonance=0.0, envelope_attack_time=0.0, envelope_release_time=0.0, envelope_amount=0.0, lfo_rate=1.0, lfo_depth=0.0, synth=None, update=True):
        Voice.set_filter(self, type, frequency, resonance, None, False)
        self.set_filter_envelope_attack_time(envelope_attack_time)
        self.set_filter_envelope_release_time(envelope_release_time)
        self.set_filter_envelope_amount(envelope_amount)
        self.set_filter_lfo_rate(lfo_rate)
        self.set_filter_lfo_depth(lfo_depth)
        if update and not synth is None: self._update_filter(synth)
