# pico_synth_sandbox/voice/__init__.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import clamp, map_value, get_filter_frequency_range, get_filter_resonance_range
import ulab.numpy as numpy
import synthio

class LerpBlockInput:
    """Creates and manages a :class:`synthio.BlockInput` object to "lerp" (linear interpolation) between an old value and a new value. Useful for note frequency "glide" and custom envelopes.

    :param rate: The speed at which to go between values, in seconds. Must be greater than 0.0s. Defaults to 0.05s.
    :type rate: float
    :param value: The initial value. Defaults to 0.0.
    :type value: float
    """

    def __init__(self, rate:float=0.05, value:float=0.0):
        """Constructor method
        """
        self.position = synthio.LFO(
            waveform=numpy.linspace(-16385, 16385, num=2, dtype=numpy.int16),
            rate=1/rate,
            scale=1.0,
            offset=0.5,
            once=True
        )
        self.lerp = synthio.Math(synthio.MathOperation.CONSTRAINED_LERP, value, value, self.position)

    def get(self) -> synthio.BlockInput:
        """Get the block input to be used with a :class:`synthio.Note` object.

        :return: linear interpolation block input
        :rtype: :class:`synthio.BlockInput`
        """
        return self.lerp
    
    def get_blocks(self) -> list[synthio.BlockInput]:
        """Get all blocks used by this object. In order for it to function properly, these blocks must be added to the primary :class:`synthio.Synthesizer` object using `synth.blocks.append(...)` or to a :class:`pico_synth_sandbox.synth.Synth` object using `synth.append(...)`.

        :return: list of blocks
        :rtype: list[:class:`synthio.BlockInput`]
        """
        return [self.position, self.lerp]
    
    def get_value(self) -> float:
        """Get the current value of the linear interpolation output.

        :return: interpolated value
        :rtype: float
        """
        return self.lerp.value
    
    def set(self, value:float):
        """Set a new value to interpolate to from the current value state. Causes the interpolation process to retrigger.

        :param value: new value
        :type value: float
        """
        self.lerp.a = self.lerp.value
        self.lerp.b = value
        self.position.retrigger()

    def set_rate(self, value:float):
        """Change the rate at which the interpolation occurs, in seconds. Must be greater than 0.0s.

        :param value: Amount of time it takes to interpolate between an old value and a new value in seconds.
        :type value: float
        """
        self.position.rate = 1/max(value, 0.001)

    def get_rate(self) -> float:
        """Get the current rate of change of interpolation. Returns as 1/seconds.

        :return: rate of change per second
        :rtype: float
        """
        return self.position.rate

class AREnvelope:
    """A simple attack, sustain and release envelope using linear interpolation. Useful for controlling parameters of a :class:`synthio.Note` object other than amplitude which accept :class:`synthio.BlockInput` values.

    :param attack: The amount of time to go from 0.0 to the specified amount in seconds when the envelope is pressed. Must be greater than 0.0s.
    :type attack: float
    :param release: The amount of time to go from the specified amount back to 0.0 in seconds when the envelope is released. Must be greater than 0.0s.
    :type release: float
    :param amount: The level at which to rise or fall to when the envelope is pressed. Value is arbitrary and can be positive or negative, but 0.0 will result in no change.
    :type amount: float
    """

    def __init__(self, attack:float=0.05, release:float=0.05, amount:float=1.0):
        """Constructor method
        """
        self._pressed = False
        self._lerp = LerpBlockInput()
        self.set_attack(attack)
        self.set_release(release)
        self.set_amount(amount)

    def get(self) -> synthio.BlockInput:
        """Get the :class:`synthio.BlockInput` object to be applied to a parameter.

        :return: envelope block input
        :rtype: :class:`synthio.BlockInput`
        """
        return self._lerp.get()
    
    def get_blocks(self) -> list[synthio.BlockInput]:
        """Get all blocks used by this object. In order for it to function properly, these blocks must be added to the primary :class:`synthio.Synthesizer` object using `synth.blocks.append(...)` or to a :class:`pico_synth_sandbox.synth.Synth` object using `synth.append(...)`.

        :return: list of blocks
        :rtype: list[:class:`synthio.BlockInput`]
        """
        return self._lerp.get_blocks()
    
    def get_value(self) -> float:
        """Get the current value of the envelope.

        :return: envelope value
        :rtype: float
        """
        return self._lerp.get_value()
    
    def is_pressed(self) -> bool:
        """Check whether or not the envelope is currently in a "pressed" state.

        :return: if the envelope is pressed
        :rtype: bool
        """
        return self._pressed
    
    def set_attack(self, value:float):
        """Change the attack time in seconds. If the envelope is currently in the attack state, it will update the rate immediately.

        :param value: The amount of time to go from 0.0 to the specified amount in seconds when the envelope is pressed. Must be greater than 0.0s.
        :type value: float
        """
        self._attack_time = value
        if self._pressed:
            self._lerp.set_rate(self._attack_time)

    def get_attack(self) -> float:
        """Get the rate of attack in seconds.

        :return: attack time in seconds
        :rtype: float
        """
        return self._attack_time
    
    def set_release(self, value):
        """Change the release time in seconds. If the envelope is currently in the release state, it will update the rate immediately.

        :param value: The amount of time to go from the specified amount back to 0.0 in seconds when the envelope is released. Must be greater than 0.0s.
        :type value: float
        """
        self._release_time = value
        if not self._pressed:
            self._lerp.set_rate(self._release_time)

    def get_release(self) -> float:
        """Get the rate of release in seconds.

        :return: release time in seconds
        :rtype: float
        """
        return self._release_time
    
    def set_amount(self, value):
        """Update the value at which the envelope will rise (or fall) to. If the envelope is currently in the attack/press state, the targeted value will be updated immediately.

        :param value: The level at which to rise or fall to when the envelope is pressed. Value is arbitrary and can be positive or negative, but 0.0 will result in no change.
        :type value: float
        """
        self._amount = value
        if self._pressed:
            self._lerp.set(self._amount)

    def get_amount(self) -> float:
        """Get the envelope amount (or sustained value).

        :return: envelope amount
        :rtype: float
        """
        return self._amount
    
    def press(self):
        """Active the envelope by setting it into the "pressed" state. The envelope's attack phase will start immediately.
        """
        self._pressed = True
        self._lerp.set_rate(self._attack_time)
        self._lerp.set(self._amount)

    def release(self):
        """Deactivate the envelope by setting it into the "released" state. The envelope's release phase will start immediately.
        """
        self._lerp.set_rate(self._release_time)
        self._lerp.set(0.0)
        self._pressed = False

class Voice:
    """A "voice" to be used with a :class:`pico_synth_sandbox.synth.Synth` object. Manages one or multiple :class:`synthio.Note` objects to be used with the primary :class:`synthio.Synthesizer` object.
    """
    
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
