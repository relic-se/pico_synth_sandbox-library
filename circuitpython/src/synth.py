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
        self.position.rate = 1/value
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
    def __init__(self, synth, root=440.0, min_filter_frequency=60.0, max_filter_frequency=20000.0):
        self._synth = synth
        self._root = root
        self._log2 = math.log(2) # for octave conversion

        self.notenum = -1
        self.velocity = 0.0

        self.velocity_amount = 1.0
        self.attack_time = 0.0
        self.decay_time = 0.0
        self.release_time = 0.0
        self.attack_level = 1.0
        self.sustain_level = 0.75

        self.filter_type = Synth.FILTER_LPF
        self._filter_type = self.filter_type
        self.filter_frequency = 1.0
        self.filter_resonance = 0.0
        self.filter_envelope = AREnvelope(self._synth)
        self.filter_lfo = synthio.LFO(
            waveform=None,
            rate=1.0,
            scale=0.0,
            offset=0.0
        )
        self._synth.append(self.filter_lfo)

        self._min_filter_frequency = min_filter_frequency
        self._max_filter_frequency = max_filter_frequency
        self._filter_buffer = ("", 0.0, 0.0)

        self.coarse_tune = 0.0
        self.fine_tune = 0.0
        self.bend_amount = 0.0
        self.bend = 0.0

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
                LerpBlockInput(self), # Frequency Lerp
                synthio.LFO( # Vibrato
                    waveform=None,
                    rate=1.0,
                    scale=0.0,
                    offset=0.0
                ),
                LerpBlockInput(self) # Pitch Bend Lerp
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

    def press(self, notenum, velocity):
        self.velocity = velocity
        self._update_envelope()
        if notenum != self.notenum:
            frequency = synthio.midi_to_hz(note)
            self.set_frequency(frequency)
            self._synth.press(self._note)
            self.filter_envelope.press()
            self.notenum = notenum
    def release(self):
        self._synth.release(self._note)
        self.filter_envelope.release()
        self.notenum = 0

    def set_frequency(self, value):
        self.frequency_lerp.set(math.log(value/self.root)/self._log2)
    def set_glide(self, value):
        self.frequency_lerp.set_rate(value)

    def set_pitch_bend_amount(self, value):
        self.bend_amount = value
        self._update_pitch_bend()
    def set_pitch_bend(self, value):
        self.bend = value
        self._update_pitch_bend()
    def _update_pitch_bend(self):
        self.pitch_bend_lerp.set(self.bend * self.bend_amount)

    def set_coarse_tune(self, value):
        self.coarse_tune = value
        self._update_root()
    def set_fine_tune(self, value):
        self.fine_tune = value
        self._update_root()
    def _update_root(self):
        self._note.frequency = self.root * pow(2,self.coarse_tune) * pow(2,self.fine_tune)

    def set_waveform(self, waveform):
        self._note.waveform = waveform

    def set_envelope(self, envelope):
        self._note.envelope = envelope
    def set_filter(self, filter):
        self._note.filter = filter

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

class Synth:
    NUM_FILTERS = 3
    FILTER_LPF = 0
    FILTER_HPF = 1
    FILTER_BPF = 2

    def __init__(self, audio, root=440.0):
        self._synth = synthio.Synthesizer(
            sample_rate=audio.get_sample_rate(),
            channel_count=12
        )
        audio.play(self._synth)

        self._voices = [Voice(self, root) for i in range(12)]

    def get_filter_types(self):
        return self._filter_types
    def build_filter(self, type, frequency, resonance):
        if type == "lpf":
            return self._synth.low_pass_filter(frequency, resonance)
        elif type == "hpf":
            return self._synth.high_pass_filter(frequency, resonance)
        else: # "bpf"
            return self._synth.band_pass_filter(frequency, resonance)

    def append(self, block):
        self._synth.blocks.append(block)
    def press(self, note):
        self._synth.press(note)
    def release(self, note):
        self._synth.release(note)
