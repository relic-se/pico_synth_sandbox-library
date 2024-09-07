# pico_synth_sandbox/voice/drum.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

# Inspired by https://gist.github.com/gamblor21/15a430929abf0e10eeaba8a45b01f5a8

from pico_synth_sandbox import clamp, map_value, calculate_filter_frequency_value
from pico_synth_sandbox.voice import Voice
from pico_synth_sandbox.synth import Synth
import pico_synth_sandbox.waveform as waveform
import synthio

class Drum(Voice):
    """Base single-shot "analog" drum voice used by other classes within the `pico_synth_sandbox.voice.drum` namespace. Handles envelope times, tuning, waveforms, etc. for multiple :class:`synthio.Note` objects.

    :param count: The number of :class:`synthio.Note` objects to generate. Defaults to 3.
    :type count: int
    :param filter_type: The type of filter to use as designated by the options within :class:`pico_synth_sandbox.synth.Synth`. Defaults to `pico_synth_sandbox.synth.Synth.FILTER_LPF` (0).
    :type filter_type: int
    :param filter_frequency: The exact frequency of the filter of all :class:`synthio.Note` objects in hertz. Defaults to 20KHz.
    :type filter_frequency: int
    :param frequencies: A list of the frequencies corresponding to each :class:`synthio.Note` object in hertz. Voice doesn't respond to the note frequency when pressed and instead uses these constant frequencies. Defaults to 440.0hz if not provided.
    :type frequencies: list[float]
    :param times: A list of decay times corresponding to each :class:`synthio.Note` objects' amplitude envelope in seconds. Defaults to 1.0s for all notes if not provided.
    :type times: list[float]
    :param waveforms: A list of waveforms corresponding to each :class:`synthio.Note` object as `numpy.int16` arrays. Can be generated using the functions within the `synthio.waveform` namespace. Defaults to a square waveform for each note.
    :type waveforms: list
    """

    def __init__(self, count:int=3, filter_type:int=Synth.FILTER_LPF, filter_frequency:int=20000, frequencies:list[float]=[], times:list[float]=[], waveforms:list=[]):
        """Constructor method
        """
        Voice.__init__(self)

        if not frequencies:
            frequencies = [440.0]
        if not times:
            times = [1.0]

        self._times = times
        self._attack_level = 1.0

        self._lfo = synthio.LFO(
            waveform=waveform.get_saw(),
            rate=20,
            scale=0.3,
            offset=0.33,
            once=True
        )

        self._notes = []
        for i in range(count):
            self._notes.append(synthio.Note(
                frequency=frequencies[i % len(frequencies)],
                bend=self._lfo
            ))

        self.set_times(times)
        self.set_waveforms(waveforms)

        self.set_filter(
            type=filter_type,
            frequency=calculate_filter_frequency_value(filter_frequency),
            resonance=0.0
        )

    def get_notes(self) -> list[synthio.Note]:
        return self._notes
    
    def get_blocks(self) -> list[synthio.BlockInput]:
        return [self._lfo]

    def set_frequencies(self, values:list[float]):
        """Set the base frequencies of the :class:`synthio.Note` objects of this voice.

        :param values: A list of the frequencies corresponding to each :class:`synthio.Note` object in hertz. Voice doesn't respond to the note frequency when pressed and instead uses these constant frequencies.
        :type values: list[float]
        """
        if isinstance(values, int): values = [values]
        if not values: return
        for i, note in enumerate(self.get_notes()):
            note.frequency = values[i % len(values)]

    def set_times(self, values:list[float]):
        """Set the decay times of the amplitude envelopes of the :class:`synthio.Note` objects of this voice.

        :param values: A list of decay times corresponding to each :class:`synthio.Note` objects' amplitude envelope in seconds.
        :type values: list[float]
        """
        if isinstance(values, int): values = [values]
        if not values: return
        self._times = values
        self._update_envelope()

    def set_waveforms(self, values:list):
        """Set the waveforms of each :class:`synthio.Note` object of this voice.

        :param values: A list of waveforms corresponding to each :class:`synthio.Note` object as `numpy.int16` arrays. Can be generated using the functions within the `synthio.waveform` namespace.
        :type values: list
        """
        if not values: return
        for i, note in enumerate(self.get_notes()):
            note.waveform = values[i % len(values)]

    def press(self, notenum:int, velocity:float=1.0) -> bool:
        """Update the voice to be "pressed" with a specific MIDI note number and velocity. Returns whether or not a new note is received. The envelope is updated with the new velocity value regardless.

        :param notenum: The MIDI note number representing the note frequency.
        :type notenum: int
        :param velocity: The strength at which the note was received, between 0.0 and 1.0.
        :type velocity: float
        :return: if a new note was received
        :rtype: bool
        """
        if not Voice.press(self, notenum, velocity):
            return False
        self._lfo.retrigger()
        return True
    
    def release(self) -> bool:
        """Release the voice if a note is currently being played. :class:`pico_synth_sandbox.voice.drum.Drum` objects typically don't implement this operation because of their "single-shot" nature and will always return `False`.

        :return: Whether or not a note was currently being played
        :rtype: bool
        """
        Voice.release(self)
        return False

    def set_level(self, value:float):
        """Change the overall volume of the voice.

        :param value: the level of the voice from 0.0 to 1.0
        :type value: float
        """
        for note in self.get_notes():
            note.amplitude = value

    def _update_envelope(self):
        mod = self._get_velocity_mod()
        for i, note in enumerate(self.get_notes()):
            note.envelope = synthio.Envelope(
                attack_time=0.0,
                decay_time=self._times[i % len(self._times)],
                release_time=0.0,
                attack_level=mod*self._attack_level,
                sustain_level=0.0
            )

    def set_envelope_attack_level(self, value:float, update:bool=True):
        """Change the level of attack in the voice amplitude envelope.

        :param value: The level of amplitude that the voice will reach when completing the attack cycle of the envelope. Value should be between 0.0 and 1.0.
        :type value: float
        :param update: Whether or not to immediately update note envelopes after updating the attack level.
        :type update: bool
        """
        self._attack_level = value
        if update: self._update_envelope()

class Kick(Drum):
    """A single-shot "analog" drum voice representing a low frequency sine-wave kick drum.
    """

    def __init__(self):
        """Constructor method
        """
        Drum.__init__(self,
            count=3,
            filter_frequency=2000,
            frequencies=[53, 72, 41],
            times=[0.075, 0.055, 0.095],
            waveforms=[waveform.get_offset_sine(), waveform.get_sine(), waveform.get_offset_sine()]
        )

class Snare(Drum):
    """A single-shot "analog" drum voice representing a snare drum using sine and noise waveforms.
    """

    def __init__(self):
        """Constructor method
        """
        Drum.__init__(self,
            count=3,
            filter_frequency=9500,
            frequencies=[90, 135, 165],
            times=[0.115, 0.095, 0.115],
            waveforms=[waveform.get_sine_noise(), waveform.get_offset_sine_noise(), waveform.get_offset_sine_noise()]
        )

class Hat(Drum):
    """The base class to create hi-hat drum sounds with variable timing.

    :param min_time: The minimum decay time in seconds. Must be greater than 0.0s.
    :type min_time: float
    :param max_time: The maximum decay time in seconds. Must be greater than `min_time`.
    :type max_time: float
    """

    def __init__(self, min_time:float, max_time:float):
        """Constructor method
        """
        Drum.__init__(self,
            count=3,
            filter_type=Synth.FILTER_HPF,
            filter_frequency=9500,
            frequencies=[90, 135, 165],
            waveforms=[waveform.get_noise()]
        )
        self._min_time = max(min_time, 0.0)
        self._max_time = max(max_time, self._min_time)
        self.set_time()

    def set_time(self, value:float=0.5):
        """Change the decay time of the hi-hat using a relative value and the predefined minimum and maximum times.

        :param value: The amount of decay time relatively from 0.0 to 1.0. Defaults to 0.5.
        :type value: float
        """
        value = map_value(value, self._min_time, self._max_time)
        self.set_times([
            value,
            clamp(value-0.02),
            value
        ])

class ClosedHat(Hat):
    """A single-shot "analog" drum voice representing a closed hi-hat cymbal using noise waveforms.
    """

    def __init__(self):
        """Constructor method
        """
        Hat.__init__(self, 0.025, 0.2)

class OpenHat(Hat):
    """A single-shot "analog" drum voice representing an open hi-hat cymbal using noise waveforms.
    """

    def __init__(self):
        """Constructor method
        """
        Hat.__init__(self, 0.25, 1.0)
