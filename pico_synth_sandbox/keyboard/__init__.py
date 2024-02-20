# pico_synth_sandbox/keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os, time
from pico_synth_sandbox.tasks import Task

class Key:
    """An abstract layer to use physical key objects with the :class:`pico_synth_sandbox.keyboard.Keyboard` class.
    """

    NONE    = 0 #: Indicates that the key hasn't been activated in any way
    PRESS   = 1 #: Indicates that the key has been pressed
    RELEASE = 2 #: Indicates that the key has been released

    def __init__(self):
        pass

    def check(self):
        """Updates any necessary logic and returns the current state of the key object.

        :return: Key state constant
        :rtype: int
        """
        return self.NONE

    def get_velocity(self):
        """Get the current velocity (0.0-1.0). Typically hard-coded at `1.0`.

        :return: Key velocity
        :rtype: float
        """
        return 1.0

class DebouncerKey(Key):
    """An abstract layer to debouncer sensor input to use physical key objects with the :class:`pico_synth_sandbox.keyboard.Keyboard` class.

    :param io_or_predicate: The input pin or arbitrary predicate to debounce
    :type io_or_predicate: ROValueIO | Callable[[], bool]
    """
    def __init__(self, io_or_predicate, invert=False):
        from adafruit_debouncer import Debouncer
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

class Note:
    def __init__(self, notenum, velocity=1.0, keynum=None):
        self.notenum = notenum
        self.velocity = velocity
        self.keynum = keynum
        self.timestamp = time.monotonic()
    def get_data(self):
        return (self.notenum, self.velocity, self.keynum)
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.notenum == other.notenum
        elif isinstance(other, Voice):
            if other.note is None:
                return False
            else:
                return self.notenum == other.note.notenum
        elif type(other) == int:
            return self.notenum == other
        elif type(other) == list:
            for i in other:
                if self.__eq__(i):
                    return True
            return False
        else:
            return False
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.notenum != other.notenum
        elif isinstance(other, Voice):
            if other.note is None:
                return True
            else:
                return self.notenum != other.note.notenum
        elif type(other) == int:
            return self.notenum != other
        elif type(other) == list:
            for i in other:
                if not self.__ne__(i):
                    return False
            return True
        else:
            return False
    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.notenum < other.notenum
        elif type(other) == int:
            return self.notenum < other
        else:
            return False
    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.notenum > other.notenum
        elif type(other) == int:
            return self.notenum > other
        else:
            return False
    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.notenum <= other.notenum
        elif type(other) == int:
            return self.notenum <= other
        else:
            return False
    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.notenum >= other.notenum
        elif type(other) == int:
            return self.notenum >= other
        else:
            return False

class Voice:
    def __init__(self, index):
        self.index = index
        self.note = None
        self.time = time.monotonic()
    def set_note(self, note):
        self.note = note
        self.time = time.monotonic()
    def is_active(self):
        return not self.note is None
    def clear(self):
        self.note = None
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.index == other.index
        elif isinstance(other, Note) or type(other) == list:
            return self.note == other
        elif type(other) is int:
            return self.index == other # NOTE: Use index or notenum?
        else:
            return False
    def __ne__(self, other):
        if isinstance(other, self.__class__):
            return self.index != other.index
        elif isinstance(other, Note) or type(other) == list:
            return self.note != other
        elif type(other) is int:
            return self.index != other # NOTE: Use index or notenum?
        else:
            return False

class Keyboard(Task):
    """Manage note allocation, arpeggiator assignment, sustain, and note callbacks using this class. The root of the keyboard (lowest note) is designated by the `KEYBOARD_ROOT` variable in `settings.toml`. The default note allocation mode is defined by the `KEYBOARD_MODE` variable in `settings.toml`. This class is inherited by the :class:`pico_synth_sandbox.keyboard.TouchKeyboard` class.

    :param keys: An array of Key objects used to include physical key inputs as notes during the update routine.
    :type keys: array
    :param max_voices: The maximum number of voices/notes to be played at once.
    :type max_voices: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    :param update_frequency: The rate at which the keyboard keys will be polled.
    :type update_frequency: float
    """

    NUM_MODES = 3 #: The number of available keyboard note allocation modes.
    MODE_HIGH = 0 #: When the keyboard is set as this mode, it will prioritize the highest note value.
    MODE_LOW  = 1 #: When the keyboard is set as this mode, it will prioritize the lowest note value.
    MODE_LAST = 2 #: When the keyboard is set as this mode, it will prioritize notes by the order in when they were played/appended.

    def __init__(self, keys=[], max_voices=1, root=None):
        if root is None:
            self.root = os.getenv("KEYBOARD_ROOT", 48)
        else:
            self.root = root
        self.keys = keys
        self._max_voices = max(max_voices, 1)

        self._notes = []
        self._voices = [Voice(i) for i in range(self._max_voices)]
        self._sustain = False
        self._sustained = []
        self._voice_press = None
        self._voice_release = None
        self._key_press = None
        self._key_release = None
        self._arpeggiator = None

        self.set_mode(os.getenv("KEYBOARD_MODE", self.MODE_HIGH))

        Task.__init__(self, update_frequency=100)

    def set_voice_press(self, callback):
        """Set the callback method you would like to be called when a voice is pressed.

        :param callback: The callback method. Must have 4 parameters for voice index, note value, velocity (0.0-1.0), and keynum (if sourced from a :class:`pico_synth_sandbox.keyboard.Key` class). Ie: `def press(voice, notenum, velocity, keynum=None):`.
        :type callback: function
        """
        self._voice_press = callback
    def set_voice_release(self, callback):
        """Set the callback method you would like to be called when a voice is released.

        :param callback: The callback method. Must have 3 parameters for voice index, note value, and keynum (if sourced from a :class:`pico_synth_sandbox.keyboard.Key` class). Velocity is always assumed to be 0.0. Ie: `def release(voice, notenum, keynum=None):`.
        :type callback: function
        """
        self._voice_release = callback
    def set_key_press(self, callback):
        """Set the callback method you would like to be called when a key is pressed.

        :param callback: The callback method. Must have 3 parameters for keynum, note value, velocity (0.0-1.0), and keynum. Ie: `def press(keynum, notenum, velocity):`.
        :type callback: function
        """
        self._key_press = callback
    def set_key_release(self, callback):
        """Set the callback method you would like to be called when a key is released.

        :param callback: The callback method. Must have 2 parameters for keynum and note value. Velocity is always assumed to be 0.0. Ie: `def release(keynum, notenum):`.
        :type callback: function
        """
        self._key_release = callback
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
        self._arpeggiator.set_press(self._timer_press)
        self._arpeggiator.set_release(self._timer_release)

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
            if note == notenum:
                return True
        return 

    def get(self, count=None):
        """Retrieve the current note allocated according to the keyboard mode. Only a single monophonic note is currently supported, but polyphony up to the initial `max_voices` value will be added in the future.

        :returns: list of `pico_synth_sandbox.keyboard.Note`
        :rtype: list
        """
        if count is None: count = self._max_voices
        notes = self.get_notes()
        if self._mode == self.MODE_HIGH or self._mode == self.MODE_LOW:
            notes.sort(reverse=(self._mode == self.MODE_HIGH))
        else: # self.MODE_LAST
            notes.sort(key=lambda note: note.timestamp)
        return notes[:count]

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
        self.remove(notenum, False, True)
        note = notenum if isinstance(notenum, Note) else Note(notenum, velocity, keynum)
        self._notes.append(note)
        if self._sustain:
            self._sustained.append(note)
        if update:
            self._update()
    def remove(self, notenum, update=True, remove_sustained=False):
        """Remove a note from the keyboard buffer. Useful when working with MIDI input or another note source. If the note is found (and the keyboard isn't being sustained or remove_sustained is set as `True`), the release callback will trigger automatically regardless of the `update` parameter.

        :param notenum: The number of the note that you would like to removed. All notes in the buffer with this value will be removed. Can be defined by MIDI notes, a designated sample index, etc.
        :type notenum: int
        :param update: Whether or not to update the keyboard logic and potentially trigger any associated callbacks.
        :type update: bool
        :param remove_sustained: Whether or not you would like to override the current sustained state of the keyboard and release any notes that are being sustained.
        :type remove_sustained: bool
        """
        if not self.has_note(notenum):
            return
        self._notes = [note for note in self._notes if note != notenum]
        if remove_sustained and self._sustain and self._sustained:
            self._sustained = [note for note in self._sustained if note != notenum]
        if update:
            self._update()

    async def update(self):
        """Update the keyboard logic and call any pre-defined callbacks if triggered. If any :class:`pico_synth_sandbox.keyboard.Key` objects (during initialization) or an :class:`pico_synth_sandbox.arpeggiator.Arpeggiator` object (using the `set_arpeggiator` method) were associated with this object, it will also be updated in this process.
        """
        if self.keys:
            for i in range(len(self.keys)):
                j = self.keys[i].check()
                if j == Key.PRESS:
                    notenum = self.root + i
                    velocity = self.keys[i].get_velocity()
                    self.append(notenum, velocity, i)
                    if self._key_press:
                        self._key_press(i, notenum, velocity)
                elif j == Key.RELEASE:
                    notenum = self.root + i
                    self.remove(notenum)
                    if self._key_release:
                        self._key_release(i, notenum)

    def _update(self):
        if not self._arpeggiator or not self._arpeggiator.is_enabled():
            self._update_voices(self.get())
        else:
            self._arpeggiator.update_notes(self.get_notes() if self.has_notes() else [])

    def _timer_press(self, notenum, velocity):
        self._update_voices(Note(notenum, velocity))
    def _timer_release(self, notenum): # NOTE: notenum is ignored
        self._update_voices()

    def get_voices(self):
        return self._voices
    
    def get_max_voices(self) -> int:
        return self._max_voices
    def set_max_voices(self, value:int):
        self._max_voices = max(value, 1)
        if len(self._voices) > self._max_voices:
            for i in range(len(self._voices) - 1, self._max_voices - 1, -1):
                self._release_voice(self._voices[i])
                del self._voices[i]
        elif len(self._voices) < self._max_voices:
            for i in range(len(self._voices), self._max_voices):
                self._voices.append(Voice(i))
        self._update_voices()

    def get_active_voices(self): # Oldest => Newest
        voices = [voice for voice in self._voices if voice.is_active()]
        voices.sort(key=lambda voice: voice.time)
        return voices
    def has_active_voice(self):
        for voice in self._voices:
            if voice.is_active():
                return True
        return False
                    
    def get_inactive_voices(self): # Oldest => Newest
        voices = [voice for voice in self._voices if not voice.is_active()]
        voices.sort(key=lambda voice: voice.time)
        return voices
    def has_inactive_voices(self):
        for voice in self._voices:
            if not voice.is_active():
                return True
        return False
    
    def _update_voices(self, notes=None):
        if isinstance(notes, Note):
            notes = [notes]
        
        # Release all active voices if no available notes
        if notes is None or not notes:
            if self.has_active_voice():
                for voice in self.get_active_voices():
                    self._release_voice(voice)
            return
        
        if self.has_active_voice():
            for voice in self.get_active_voices():
                # Determine if voice has one of the notes in the buffer
                has_note = False
                for note in notes:
                    if voice.note is note:
                        has_note = True
                        break
                if not has_note:
                    # Release voices without active notes
                    self._release_voice(voice)
                else:
                    # Remove currently active notes from buffer
                    notes.remove(voice.note)

        if not notes:
            return # No new notes
        
        # Activate new notes
        if self.has_inactive_voices(): # If no voices are available, it will ignore remaining notes
            voices = self.get_inactive_voices()
            voice_index = 0
            for note in notes:
                self._press_voice(voices[voice_index], note)
                voice_index += 1
                if voice_index >= len(voices):
                    break

    def _press_voice(self, voice, note):
        voice.set_note(note)
        if self._voice_press:
            self._voice_press(voice.index, voice.note.notenum, voice.note.velocity, voice.note.keynum)
    def _release_voice(self, voice:Voice):
        if type(voice) is list:
            for i in voice:
                self._release_voice(i)
        elif voice.is_active():
            if self._voice_release:
                self._voice_release(voice.index, voice.note.notenum, voice.note.keynum)
            voice.clear()

def get_keyboard_driver(board, max_voices=1, root=None):
    """Automatically generate the proper :class:`pico_synth_sandbox.keyboard.Keyboard` object based on the device's settings.toml configuration.

    :param max_voices: The maximum number of voices/notes to be played at once.
    :type max_voices: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    """
    if board.has_touch_keys():
        from pico_synth_sandbox.keyboard.touch import TouchKeyboard
        return TouchKeyboard(
            board,
            max_voices=max_voices,
            root=root
        )
    elif board.has_ttp():
        from pico_synth_sandbox.keyboard.ton_touch import TonTouchKeyboard
        return TonTouchKeyboard(
            board,
            max_voices=max_voices,
            root=root,
            input_mode=TonTouchKeyboard.MODE_8KEY if board.get_ttp_mode() == "TTP8" else TonTouchKeyboard.MODE_16KEY
        )
    else:
        return Keyboard(
            max_voices=max_voices,
            root=root
        )
