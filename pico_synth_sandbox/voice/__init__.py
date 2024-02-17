# pico_synth_sandbox/voice/__init__.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import clamp, map_value, get_filter_frequency_range, get_filter_resonance_range
import ulab.numpy as numpy
import synthio

class LerpBlockInput:
    def __init__(self, rate=0.05, value=0.0):
        self.position = synthio.LFO(
            waveform=numpy.linspace(-16385, 16385, num=2, dtype=numpy.int16),
            rate=1/rate,
            scale=1.0,
            offset=0.5,
            once=True
        )
        self.lerp = synthio.Math(synthio.MathOperation.CONSTRAINED_LERP, value, value, self.position)
    def get(self):
        return self.lerp
    def get_blocks(self):
        return [self.position, self.lerp]
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
    def __init__(self, attack=0.05, release=0.05, amount=1.0):
        self._pressed = False
        self._lerp = LerpBlockInput()
        self.set_attack(attack)
        self.set_release(release)
        self.set_amount(amount)
    def get(self):
        return self._lerp.get()
    def get_blocks(self):
        return self._lerp.get_blocks()
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
    def __init__(self):
        self._notenum = -1
        self._velocity = 0.0

        self._filter_type = 0
        self._filter_frequency = 1.0
        self._filter_resonance = 0.0
        self._filter_buffer = ("", 0.0, 0.0)

        self._velocity_amount = 1.0

    def get_notes(self):
        return []
    def get_blocks(self):
        return []

    def press(self, notenum, velocity=1.0):
        self._velocity = velocity
        self._update_envelope()
        if notenum == self._notenum: return False
        self._notenum = notenum
        return True
    def release(self):
        if self._notenum <= 0: return False
        self._notenum = 0
        return True

    def set_level(self, value):
        pass

    # Velocity
    def _get_velocity_mod(self):
        return 1.0 - (1.0 - clamp(self._velocity)) * self._velocity_amount
    def set_velocity_amount(self, value):
        self._velocity_amount = value
    def _update_envelope(self):
        pass

    # Filter
    def _get_filter_type(self):
        return self._filter_type
    def _get_filter_frequency_value(self):
        return self._filter_frequency
    def _get_filter_frequency(self, sample_rate=None):
        range = get_filter_frequency_range(sample_rate)
        return map_value(self._get_filter_frequency_value(), range[0], range[1])
    def _get_filter_resonance(self):
        range = get_filter_resonance_range()
        return map_value(self._filter_resonance, range[0], range[1])

    def _update_filter(self, synth):
        type = self._get_filter_type()
        frequency = self._get_filter_frequency(synth.get_sample_rate())
        resonance = self._get_filter_resonance()

        if self._filter_buffer[0] == type and self._filter_buffer[1] == frequency and self._filter_buffer[2] == resonance:
            return
        self._filter_buffer = (type, frequency, resonance)

        filter = synth.build_filter(type, frequency, resonance)
        for note in self.get_notes():
            note.filter = filter

    def set_filter_type(self, value, synth=None, update=True):
        self._filter_type = value
        if update and not synth is None: self._update_filter(synth)
    def set_filter_frequency(self, value, synth=None, update=True):
        self._filter_frequency = value
        if update and not synth is None: self._update_filter(synth)
    def set_filter_resonance(self, value, synth=None, update=True):
        self._filter_resonance = value
        if update and not synth is None: self._update_filter(synth)
    def set_filter(self, type=0, frequency=1.0, resonance=0.0, synth=None, update=True):
        self.set_filter_type(type, update=False)
        self.set_filter_frequency(frequency, update=False)
        self.set_filter_resonance(resonance, update=False)
        if update and not synth is None: self._update_filter(synth)

    # Loop
    async def update(self, synth):
        self._update_filter(synth)
