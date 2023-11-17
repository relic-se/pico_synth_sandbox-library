# pico_synth_sandbox/keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os
from pico_synth_sandbox.tasks import Task
from adafruit_debouncer import Debouncer

# TODO: Add Output Buffer Voices

class Key:
    """An abstract layer to use physical key objects with the :class:`pico_synth_sandbox.keyboard.Keyboard` class.
    """

    NONE=0 #: Indicates that the key hasn't been activated in any way
    PRESS=1 #: Indicates that the key has been pressed
    RELEASE=2 #: Indicates that the key has been released

    def __init__(self):
        pass

    def check(self):
        """Updates any necessary logic and returns the current state of the key object.

        :return: Key state constant
        :rtype: int
        """
        return self.NONE

class DebouncerKey(Key):
    """An abstract layer to debouncer sensor input to use physical key objects with the :class:`pico_synth_sandbox.keyboard.Keyboard` class.

    :param io_or_predicate: The input pin or arbitrary predicate to debounce
    :type io_or_predicate: ROValueIO | Callable[[], bool]
    """
    def __init__(self, io_or_predicate, invert=False):
        self._debouncer = Debouncer(io_or_predicate)
        self._inverted = invert

    def check(self):
        """Updates the input pin or arbitraary predicate with basic debouncing and returns the current key state.

        :return: Key state constant
        :rtype: int
        """
        self._debouncer.update()
        if self._debouncer.rose:
            return self.PRESS if not self._inverted else self.RELEASE
        elif self._debouncer.fell:
            return self.RELEASE if not self._inverted else self.PRESS
        else:
            return self.NONE

class Keyboard(Task):
    """Manage note allocation, arpeggiator assignment, sustain, and note callbacks using this class. The root of the keyboard (lowest note) is designated by the `KEYBOARD_ROOT` variable in `settings.toml`. The default note allocation mode is defined by the `KEYBOARD_MODE` variable in `settings.toml`. This class is inherited by the :class:`pico_synth_sandbox.keyboard.TouchKeyboard` class.

    :param keys: An array of Key objects used to include physical key inputs as notes during the update routine.
    :type keys: array
    :param max_notes: The maximum number of notes to be played at once. Currently, this feature is not implemented. When using the `get` method, the result is monophonic (1 note).
    :type max_notes: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    :param update_frequency: The rate at which the keyboard keys will be polled.
    :type update_frequency: float
    """

    NUM_MODES=3 #: The number of available keyboard note allocation modes.
    MODE_HIGH=0 #: When the keyboard is set as this mode, it will prioritize the highest note value.
    MODE_LOW=1 #: When the keyboard is set as this mode, it will prioritize the lowest note value.
    MODE_LAST=2 #: When the keyboard is set as this mode, it will prioritize notes by the order in when they were played/appended.

    def __init__(self, keys=[], max_notes=1, root=None):
        if root is None:
            self.root = os.getenv("KEYBOARD_ROOT", 48)
        else:
            self.root = root
        self.keys = keys
        self.max_notes = max(max_notes, 1) # Not implemented

        self._notes = []
        self._sustain = False
        self._sustained = []
        self._press = None
        self._release = None
        self._arpeggiator = None

        self.set_mode(os.getenv("KEYBOARD_MODE", self.MODE_HIGH))

        Task.__init__(self, update_frequency=100)

    def set_press(self, callback):
        """Set the callback method you would like to be called when a new note is pressed.

        :param callback: The callback method. Must have 3 parameters for note value, velocity (0.0-1.0), and keynum (if sourced from a :class:`pico_synth_sandbox.keyboard.Key` class). Ie: `def press(notenum, velocity, keynum=None):`.
        :type callback: function
        """
        self._press = callback
        if self._arpeggiator:
            self._arpeggiator.set_press(callback)
    def set_release(self, callback):
        """Set the callback method you would like to be called when a note is released.

        :param callback: The callback method. Must have 2 parameters for note value, and keynum (if sourced from a :class:`pico_synth_sandbox.keyboard.Key` class). Velocity is always assumed to be 0.0. Ie: `def release(notenum, keynum=None):`.
        :type callback: function
        """
        self._release = callback
        if self._arpeggiator:
            self._arpeggiator.set_release(callback)
    def set_arpeggiator(self, arpeggiator):
        """Assign an arpeggiator class to the keyboard. Must be of type :class:`pico_synth_sandbox.arpeggiator.Arpeggiator` or a child of that class. When notes are appended to this object, the arpeggiator will automatically be updated. Callbacks from the arpeggiator will also be routed through the press and release callbacks of this object.

        :param arpeggiator: The arpeggiator object to be assigned ot the keyboard. If this class is called multiple times, the callbacks of the previously allocated arpeggiator will be unassigned.
        :type callback: :class:`pico_synth_sandbox.arpeggiator.Arpeggiator`
        """
        if self._arpeggiator:
            self._arpeggiator.set_press(None)
            self._arpeggiator.set_release(None)
        self._arpeggiator = arpeggiator
        self._arpeggiator.set_keyboard(self)
        if self._press:
            self._arpeggiator.set_press(self._press)
        if self._release:
            self._arpeggiator.set_release(self._release)

    def get_mode(self):
        """Get the current note allocation mode of this object.

        :return: keyboard mode
        :rtype: int
        """
        return self._mode
    def set_mode(self, value):
        """Set the note allocation mode of this object. Use one of the mode constants of this class such as `pico_synth_sandbox.Keyboard.MODE_HIGH`. Note allocation won't be updated until the next update call.

        :param value: The desired mode type.
        :type value: int
        """
        self._mode = value % self.NUM_MODES

    def get_sustain(self):
        """Get the current sustain state of the keyboard.

        :return: sustain
        :rtype: bool
        """
        return self._sustain
    def set_sustain(self, value, update=True):
        """Set the sustain state of the keyboard. If sustain is set as `True`, it will prevent current and future notes from being released until sustain is set as `False`.

        :param value: The desired state of sustain. If sustain is set as `False`, any notes that are no longer being held will be released immediately.
        :type value: bool
        :param update: Whether or not you would like to update the current list notes after changing the sustained state. This may trigger a new note press according to the note allocation rules immediately.
        """
        if value != self._sustain:
            self._sustain = value

            # Release any missing notes
            if not self._sustain and self._sustained:
                for note in self._sustained:
                    found = False
                    if not self.has_note(note[0], False) and self._release:
                        self._release(note[0], note[2])

            self._sustained = []
            if self._sustain:
                self._sustained = self._notes.copy()

            if update:
                self._update()

    def has_notes(self, include_sustained=True):
        """Check whether the keyboard has any active notes.

        :param include_sustained: If set as `True`, any sustained notes (if sustain is active) will be included in the check.
        :type include_sustained: bool
        :returns: has notes
        :rtype: bool
        """
        if include_sustained and self._sustain and self._sustained:
            return True
        if self._notes:
            return True
        return False
    def get_notes(self, include_sustained=True):
        """Get all active notes in the keyboard object. Notes are tuples with 3 elements of `(notenum, velocity, keynum)`. `keynum` may be set as None if note came from an external source instead of a :class:`pico_synth_sandbox.keyboard.Key` object.

        :param include_sustained: If set as `True`, any sustained notes will be included in the returned value.
        :type include_sustained: bool
        :returns: note tuples
        :rtype: array
        """
        if not self.has_notes(include_sustained):
            return []
        if include_sustained:
            return (self._notes if self._notes else []) + (self._sustained if self._sustain and self._sustained else [])
        else:
            return self._notes

    def has_note(self, notenum, include_sustained=True):
        """Check whether the keyboard has an active note of a particular note value.

        :param include_sustained: If set as `True`, any sustained notes (if sustain is active) will be included in the check.
        :type include_sustained: bool
        :returns: has note
        :rtype: bool
        """
        for note in self.get_notes(include_sustained):
            if note[0] == notenum:
                return True
        return False

    def _get_low(self):
        if not self.has_notes():
            return None
        selected = (127, 0)
        if self._notes:
            for note in self._notes:
                if note[0] < selected[0]:
                    selected = note
        if self._sustain and self._sustained:
            for note in self._sustained:
                if note[0] < selected[0]:
                    selected = note
        return selected
    def _get_high(self):
        if not self.has_notes():
            return None
        selected = (0, 0)
        if self._notes:
            for note in self._notes:
                if note[0] > selected[0]:
                    selected = note
        if self._sustain and self._sustained:
            for note in self._sustained:
                if note[0] > selected[0]:
                    selected = note
        return selected
    def _get_last(self):
        if self._sustain and self._sustained:
            return self._sustained[-1]
        if self._notes:
            return self._notes[-1]
        return None
    def get(self):
        """Retrieve the current note allocated according to the keyboard mode. Only a single monophonic note is currently supported, but polyphony up to the initial `max_notes` value will be added in the future.

        :returns: note as (notenum, velocity, keynum)
        :rtype: tuple
        """
        if self._mode == self.MODE_HIGH:
            return self._get_high()
        elif self._mode == self.MODE_LOW:
            return self._get_low()
        else: # self.MODE_LAST
            return self._get_last()

    def append(self, notenum, velocity=1.0, keynum=None, update=True):
        """Add a note to the keyboard buffer. Useful when working with MIDI input or another note source. Any previous notes with the same notenum value will be removed automatically.

        :param notenum: The number of the note. Can be defined by MIDI notes, a designated sample index, etc. When using MODE_HIGH or MODE_LOW, the value of this parameter will affect the order.
        :type notenum: int
        :param velocity: The velocity of the note from 0.0 through 1.0.
        :type velocity: float
        :param keynum: An additional index reference typically used to associate the note with a physical :class:`pico_synth_sandbox.keyboard.Key` object. Not required for use of the keyboard.
        :type keynum: int
        :param update: Whether or not to update the keyboard logic and potentially trigger any associated callbacks.
        :type update: bool
        """
        self.remove(notenum, None, False, True)
        note = (notenum, velocity, keynum)
        self._notes.append(note)
        if self._sustain:
            self._sustained.append(note)
        if update:
            self._update()
    def remove(self, notenum, keynum=None, update=True, remove_sustained=False):
        """Remove a note from the keyboard buffer. Useful when working with MIDI input or another note source. If the note is found (and the keyboard isn't being sustained or remove_sustained is set as `True`), the release callback will trigger automatically regardless of the `update` parameter.

        :param notenum: The number of the note that you would like to removed. All notes in the buffer with this value will be removed. Can be defined by MIDI notes, a designated sample index, etc.
        :type notenum: int
        :param keynum: An additional index reference typically used to associate the note with a physical :class:`pico_synth_sandbox.keyboard.Key` object. This value will be used in the release callback if triggered. Not required for use of the keyboard.
        :type keynum: int
        :param update: Whether or not to update the keyboard logic and potentially trigger any associated callbacks.
        :type update: bool
        :param remove_sustained: Whether or not you would like to override the current sustained state of the keyboard and release any notes that are being sustained.
        :type remove_sustained: bool
        """
        if not self.has_note(notenum):
            return
        self._notes = [note for note in self._notes if note[0] != notenum]
        if remove_sustained and self._sustain and self._sustained:
            self._sustained = [note for note in self._sustained if note[0] != notenum]
        if self._release and (remove_sustained or not self.has_note(notenum)):
            self._release(notenum, keynum)
        if update:
            self._update()

    def update(self):
        """Update the keyboard logic and call any pre-defined callbacks if triggered. If any :class:`pico_synth_sandbox.keyboard.Key` objects (during initialization) or an :class:`pico_synth_sandbox.arpeggiator.Arpeggiator` object (using the `set_arpeggiator` method) were associated with this object, it will also be updated in this process.
        """
        if self.keys:
            for i in range(len(self.keys)):
                j = self.keys[i].check()
                if j == Key.PRESS:
                    self.append(self.root + i, 1.0, i) # Velocity is hard-coded
                elif j == Key.RELEASE:
                    self.remove(self.root + i, i)

    def _update(self):
        if not self._arpeggiator or not self._arpeggiator.is_enabled():
            note = self.get()
            if note and self._press:
                self._press(note[0], note[1], note[2])
        elif self.has_notes():
            self._arpeggiator.update_notes(self.get_notes())
        else:
            self._arpeggiator.update_notes()

def get_keyboard_driver(max_notes=1, root=None):
    """Automatically generate the proper :class:`pico_synth_sandbox.keyboard.Keyboard` object based on the device's settings.toml configuration.

    :param max_notes: The maximum number of notes to be played at once. Currently, this feature is not implemented. When using the `get` method, the result is monophonic (1 note).
    :type max_notes: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    """
    driver = os.getenv("KEYBOARD_DRIVER", "TTP")
    if driver == "TOUCH":
        from pico_synth_sandbox.keyboard.touch import TouchKeyboard
        return TouchKeyboard(
            max_notes=max_notes,
            root=root
        )
    elif driver.startswith("TTP"):
        from pico_synth_sandbox.keyboard.ton_touch import TonTouchKeyboard
        return TonTouchKeyboard(
            max_notes=max_notes,
            root=root,
            input_mode=TonTouchKeyboard.MODE_8KEY if driver == "TTP8" else TonTouchKeyboard.MODE_16KEY
        )
    else:
        return Keyboard(
            max_notes=max_notes,
            root=root
        )
