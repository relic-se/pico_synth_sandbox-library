class LerpBlockInput:
    def __init__(self, synth, rate=0.05, value=0.0):
        self.position = synthio.LFO(
            waveform=numpy.linspace(-16385, 16385, num=2, dtype=numpy.int16),
            rate=1/rate,
            scale=1.0,
            offset=0.5,
            once=True
        )
        synth.append(self.position)
        self.lerp = synthio.Math(synthio.MathOperation.CONSTRAINED_LERP, value, value, self.position)
        synth.append(self.lerp)
    def get(self):
        return self.lerp
    def get_value(self):
        return self.lerp.value
    def set(self, value):
        self.lerp.a = self.lerp.value
        self.lerp.b = value
        self.position.retrigger()
    def set_rate(self, value):
        self.position.rate = 1/max(value, 0.001)
    def get_rate(self):
        return self.position.rate

class AREnvelope:
    def __init__(self, synth, attack=0.05, release=0.05, amount=1.0):
        self._pressed = False
        self._lerp = LerpBlockInput(synth)
        self.set_attack(attack)
        self.set_release(release)
        self.set_amount(amount)
    def get(self):
        return self._lerp.get()
    def get_value(self):
        return self._lerp.get_value()
    def is_pressed(self):
        return self._pressed
    def set_attack(self, value):
        self._attack_time = value
        if self._pressed:
            self._lerp.set_rate(self._attack_time)
    def get_attack(self):
        return self._attack_time
    def set_release(self, value):
        self._release_time = value
        if not self._pressed:
            self._lerp.set_rate(self._release_time)
    def get_release(self):
        return self._release_time
    def set_amount(self, value):
        self._amount = value
        if self._pressed:
            self._lerp.set(self._amount)
    def get_amount(self):
        return self._amount
    def press(self):
        self._pressed = True
        self._lerp.set_rate(self._attack_time)
        self._lerp.set(self._amount)
    def release(self):
        self._lerp.set_rate(self._release_time)
        self._lerp.set(0.0)
        self._pressed = False

class Voice:
    def __init__(self, synth, root=440.0, min_filter_frequency=60.0, max_filter_frequency=20000.0, min_filter_resonance=0.5, max_filter_resonance=8.0):
        self._synth = synth
        self._root = root
        self._log2 = math.log(2) # for octave conversion

        self._notenum = -1
        self._velocity = 0.0

        self._filter_type = Synth.FILTER_LPF
        self._filter_frequency = 1.0
        self._filter_resonance = 0.0
        self._filter_envelope = AREnvelope(self._synth)
        self._filter_lfo = synthio.LFO(
            waveform=None,
            rate=1.0,
            scale=0.0,
            offset=0.0
        )
        synth.append(self._filter_lfo)

        self._min_filter_frequency = min_filter_frequency
        self._max_filter_frequency = min(max_filter_frequency, synth.get_sample_rate() * 0.45)
        self._min_filter_resonance = min_filter_resonance
        self._max_filter_resonance = max_filter_resonance
        self._filter_buffer = ("", 0.0, 0.0)

        self.coarse_tune = 0.0
        self.fine_tune = 0.0
        self.bend_amount = 0.0
        self.bend = 0.0

        self._velocity_amount = 1.0
        self._attack_time = 0.0
        self._decay_time = 0.0
        self._release_time = 0.0
        self._attack_level = 1.0
        self._sustain_level = 0.75

        self._freq_lerp = LerpBlockInput(synth)
        self._pitch_lerp = LerpBlockInput(synth)
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
        synth.append(self._note.amplitude)
        synth.append(self._note.bend)
        synth.append(self._note.panning)

    def get(self):
        return self._note

    def press(self, notenum, velocity=100):
        self._velocity = velocity
        self._update_envelope()
        if notenum != self._notenum:
            frequency = synthio.midi_to_hz(notenum)
            self.set_frequency(frequency)
            self._synth.press(self._note)
            self._filter_envelope.press()
            self._notenum = notenum
    def release(self):
        self._synth.release(self._note)
        self._filter_envelope.release()
        self._notenum = 0

    def set_frequency(self, value):
        self._freq_lerp.set(math.log(value/self._root)/self._log2)
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
    def _get_velocity_mod(self):
        return 1.0 - (1.0 - min(max(self._velocity, 0.0), 1.0)) * self._velocity_amount
    def _build_envelope(self):
        mod = self._get_velocity_mod()
        return synthio.Envelope(
            attack_time=self._attack_time,
            decay_time=self._decay_time,
            release_time=self._release_time,
            attack_level=mod*self._attack_level,
            sustain_level=mod*self._sustain_level
        )
    def _update_envelope(self):
        self._note.envelope = self._build_envelope()
    def set_velocity_amount(self, value):
        self._velocity_amount = value
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
    def _update_filter(self):
        type = min(max(self._filter_type, 0), Synth.NUM_FILTERS - 1)
        frequency = min(max(self._filter_frequency + self._filter_envelope.get_value() + self._filter_lfo.value, 0.0), 1.0) * (self._max_filter_frequency - self._min_filter_frequency) + self._min_filter_frequency
        resonance = min(max(self._filter_resonance, 0.0), 1.0) * (self._max_filter_resonance - self._min_filter_resonance) + self._min_filter_resonance

        if self._filter_buffer[0] == type and self._filter_buffer[1] == frequency and self._filter_buffer[2] == resonance:
            return
        self._filter_buffer = (type, frequency, resonance)

        self._note.filter = self._synth.build_filter(type, frequency, resonance)
    def set_filter_type(self, value, update=True):
        self._filter_type = value
        if update: self._update_filter()
    def set_filter_frequency(self, value, update=True):
        self._filter_frequency = value
        if update: self._update_filter()
    def set_filter_resonance(self, value, update=True):
        self._filter_resonance = value
        if update: self._update_filter()
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
    def set_filter(self, type=0, frequency=1.0, resonance=0.0, envelope_attack_time=0.0, envelope_release_time=0.0, envelope_amount=0.0, lfo_rate=1.0, lfo_depth=0.0, update=True):
        self.set_filter_type(type, False)
        self.set_filter_frequency(frequency, False)
        self.set_filter_resonance(resonance, False)
        self.set_filter_envelope_attack_time(envelope_attack_time)
        self.set_filter_envelope_release_time(envelope_release_time)
        self.set_filter_envelope_amount(envelope_amount)
        self.set_filter_lfo_rate(lfo_rate)
        self.set_filter_lfo_depth(lfo_depth)
        if update: self._update_filter()

    # Loop
    def update(self):
        self._update_filter()
