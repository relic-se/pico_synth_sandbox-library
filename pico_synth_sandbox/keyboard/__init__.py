# pico_synth_sandbox/keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os, time
from pico_synth_sandbox.tasks import Task
from adafruit_debouncer import Debouncer

class Key:
    """An abstract layer to use physical key objects with the :class:`pico_synth_sandbox.keyboard.Keyboard` class.
    """

    NONE:int    = 0
    """int: Indicates that the key hasn't been activated in any way
    """
    PRESS:int   = 1
    """int: Indicates that the key has been pressed
    """
    RELEASE:int = 2
    """int: Indicates that the key has been released
    """

    def __init__(self):
        """Constructor method
        """
        pass

    def check(self) -> int:
        """Updates any necessary logic and returns the current state of the key object.

        :return: Key state constant
        :rtype: int
        """
        return self.NONE

    def get_velocity(self) -> float:
        """Get the current velocity (0.0-1.0). Typically hard-coded at `1.0`.

        :return: Key velocity
        :rtype: float
        """
        return 1.0

class DebouncerKey(Key):
    """An abstract layer to debouncer sensor input to use physical key objects with the :class:`pico_synth_sandbox.keyboard.Keyboard` class.

    :param io_or_predicate: The input pin or arbitrary predicate to debounce
    :type io_or_predicate: ROValueIO | Callable[[], bool]
    :int invert: Whether or not to invert the state of the input. When invert is `False`, the signal is active-high. When it is `True`, the signal is active-low. Defaults to `False`.
    :type invert: bool
    """

    def __init__(self, io_or_predicate, invert:bool=False):
        """Constructor method
        """
        self._debouncer = Debouncer(io_or_predicate)
        self._inverted = invert

    def check(self) -> int:
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
    """Object which represents the parameters of a note. Contains note number, velocity, key number (if evoked by a :class:`pico_synth_sandbox.keyboard.Key` object), and timestamp of when the note was created.

    :param notenum: The MIDI note number representing the frequency of a note.
    :type notenum: int
    :param velocity: The strength of which a note was pressed. Ranges from 0.0 to 1.0. Defaults to 1.0.
    :type velocity: float
    :param keynum: The index number of the :class:`pico_synth_sandbox.keyboard.Key` object which may have created this :class:`pico_synth_sandbox.keyboard.Note` object. If not applicable, will be `None`. Defaults to `None`.
    """

    def __init__(self, notenum:int, velocity:float=1.0, keynum:int=None):
        """Constructor method
        """
        self.notenum = notenum
        self.velocity = velocity
        self.keynum = keynum
        self.timestamp = time.monotonic()

    def get_data(self) -> tuple[int, float, int]:
        """Return all note data as tuple. The data is formatted as: (notenum:int, velocity:float, keynum:int). Keynum may be set as `None` if not applicable.

        :return: note data
        :rtype: tuple[int, float, int]
        """
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
    """Object which represents the parameters of a :class:`pico_synth_sandbox.keyboard.Keyboard` voice. Used to allocate :class:`pico_synth_sandbox.keyboard.Note` objects to a pre-defined number of available slots in a logical manner based on timing and keyboard mode.

    :param index: The position of the voice in the pre-defined set of keyboard voices. Used for external reference.
    :type index: int
    """

    def __init__(self, index:int):
        """Constructor method
        """
        self.index = index
        self.note = None
        self.time = time.monotonic()

    def set_note(self, note:Note):
        """Assign a :class:`pico_synth_sandbox.keyboard.Note` object to a voice. When a note is assigned to a voice, the voice is "active" until the note is cleared.

        :param note: The :class:`pico_synth_sandbox.keyboard.Note` object
        :type note: :class:`pico-synth_sandbox.keyboard.Note`
        """
        self.note = note
        self.time = time.monotonic()

    def is_active(self) -> bool:
        """Determines whether or not a voice has a :class:`pico_synth_sandbox.keyboard.Note` object assigned to it. If it does, it will return `True`. Otherwise, `False`.

        :return: the active state of the voice
        :rtype: bool
        """
        return not self.note is None
    
    def clear(self):
        """Remove any assigned :class:`pico_synth_sandbox.keyboard.Note` object from the voice. The voice will be made "inactive".
        """
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
    """Manage notes, voice allocation, arpeggiator assignment, sustain, and relevant callbacks using this class. The default note allocation mode is defined by the `KEYBOARD_MODE` variable in `settings.toml`.

    :param keys: A list of :class:`pico_synth_sandbox.keyboard.Key` objects used to include physical key inputs as notes during the update routine.
    :type keys: list
    :param max_voices: The maximum number of voices/notes to be played at once.
    :type max_voices: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    """

    NUM_MODES = 3
    """int: The number of available keyboard note allocation modes.
    """
    MODE_HIGH = 0
    """int: When the keyboard is set as this mode, it will prioritize the highest note value.
    """
    MODE_LOW  = 1
    """int: When the keyboard is set as this mode, it will prioritize the lowest note value.
    """
    MODE_LAST = 2
    """int: When the keyboard is set as this mode, it will prioritize notes by the order in when they were played/appended.
    """

    def __init__(self, keys:list[Key]=[], max_voices:int=1, root:int=None):
        """Constructor method
        """
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

    def get_mode(self) -> int:
        """Get the current note allocation mode of this object.

        :return: keyboard mode
        :rtype: int
        """
        return self._mode
    def set_mode(self, value:int):
        """Set the note allocation mode of this object. Use one of the mode constants of this class such as `pico_synth_sandbox.Keyboard.MODE_HIGH`. Note allocation won't be updated until the next update call.

        :param value: The desired mode type.
        :type value: int
        """
        self._mode = value % self.NUM_MODES

    def get_sustain(self) -> bool:
        """Get the current sustain state of the keyboard.

        :return: sustain
        :rtype: bool
        """
        return self._sustain
    def set_sustain(self, value:bool, update:bool=True):
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

    def has_notes(self, include_sustained:bool=True) -> bool:
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
    def get_notes(self, include_sustained:bool=True) -> list[Note]:
        """Get all active :class:`pico_synth_sandbox.keyboard.Note` objects within the keyboard object.

        :param include_sustained: If set as `True`, any sustained notes will be included in the returned value.
        :type include_sustained: bool
        :returns: list of note objects
        :rtype: list[:class:`pico_synth_sandbox.keyboard.Note`]
        """
        if not self.has_notes(include_sustained):
            return []
        if include_sustained:
            return (self._notes if self._notes else []) + (self._sustained if self._sustain and self._sustained else [])
        else:
            return self._notes

    def has_note(self, notenum:int|Note, include_sustained:bool=True) -> bool:
        """Check whether the keyboard has an active note.

        :param notenum: The MIDI note value or :class:`pico_synth_sandbox.keyboard.Note` to check for.
        :type notenum: int|:class:`pico_synth_sandbox.keyboard.Note`
        :param include_sustained: If set as `True`, any sustained notes (if sustain is active) will be included in the check.
        :type include_sustained: bool
        :returns: has note
        :rtype: bool
        """
        for note in self.get_notes(include_sustained):
            if note == notenum:
                return True
        return False

    def get(self, count:int=None) -> list[Note]:
        """Retrieve a set of active notes according to the keyboard mode setting (`MODE_HIGH`, `MODE_LOW`, or `MODE_LAST`).

        :param count: The number of notes to return. If left undefined, the max voices setting of the keyboard object will be used instead.
        :type count: int
        :returns: list of `pico_synth_sandbox.keyboard.Note` objects
        :rtype: list[:class:`pico_synth_sandbox.keyboard.Note`]
        """
        if count is None: count = self._max_voices
        notes = self.get_notes()
        if self._mode == self.MODE_HIGH or self._mode == self.MODE_LOW:
            notes.sort(reverse=(self._mode == self.MODE_HIGH))
        else: # self.MODE_LAST
            notes.sort(key=lambda note: note.timestamp)
        return notes[:count]

    def append(self, notenum:int|Note, velocity:float=1.0, keynum:int=None, update:bool=True):
        """Add a note to the keyboard buffer. Useful when working with MIDI input or another note source. Any previous notes with the same notenum value will be removed automatically.

        :param notenum: The number of the note. Can be defined by MIDI notes, a designated sample index, etc. When using MODE_HIGH or MODE_LOW, the value of this parameter will affect the order. A :class:`pico_synth_sandbox.keyboard.Note` object can be used instead of providing notenum, velocity, and keynum parameters directly.
        :type notenum: int|:class:`pico_synth_sandbox.keyboard.Note`
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
        
    def remove(self, notenum:int|Note, update:bool=True, remove_sustained:bool=False):
        """Remove a note from the keyboard buffer. Useful when working with MIDI input or another note source. If the note is found (and the keyboard isn't being sustained or remove_sustained is set as `True`), the release callback will trigger automatically regardless of the `update` parameter.

        :param notenum: The value of the note that you would like to be removed. All notes in the buffer with this value will be removed. Can be defined by MIDI note value, a designated sample index, etc. Can also use a :class:`pico_synth_sandbox.keyboard.Note` object instead.
        :type notenum: int|:class:`pico_synth_sandbox.keyboard.Note`
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

    def get_voices(self) -> list[Voice]:
        """Get all :class:`pico_synth_sandbox.keyboard.Voice` objects used by the :class:`pico_synth_sandbox.keyboard.Keyboard` object.

        :return: list of voice objects
        :rtype: list[:class:`pico_synth_sandbox.keyboard.Voice`]
        """
        return self._voices
    
    def get_max_voices(self) -> int:
        """Return the maximum number of voices used by this keyboard to allocate notes.

        :return: max voices
        :rtype: int
        """
        return self._max_voices
    def set_max_voices(self, value:int):
        """Change the number of max voices used to allocate notes. Must be greater than 1. When this method is called, it will automatically release and delete any voices or add new voice objects depending on the previous number of voices. Any voice related callbacks may be triggered during this process.

        :param value: The maximum number of voices to allocate notes
        :type value: int
        """
        self._max_voices = max(value, 1)
        if len(self._voices) > self._max_voices:
            for i in range(len(self._voices) - 1, self._max_voices - 1, -1):
                self._release_voice(self._voices[i])
                del self._voices[i]
        elif len(self._voices) < self._max_voices:
            for i in range(len(self._voices), self._max_voices):
                self._voices.append(Voice(i))
        self._update_voices()

    def get_active_voices(self) -> list[Voice]:
        """Get all keyboard voices that are "active", have been assigned a note. The voices will automatically be sorted by the time they were last assigned a note from oldest to newest.

        :return: all active voices
        :rtype: list[:class:`pico_synth_sandbox.keyboard.Voice`]
        """
        voices = [voice for voice in self._voices if voice.is_active()]
        voices.sort(key=lambda voice: voice.time)
        return voices
    def has_active_voice(self) -> bool:
        """Checks to see if any voice is currently "active", has been assigned a note.

        :return: whether or not at least one voice is active
        :rtype: bool
        """
        for voice in self._voices:
            if voice.is_active():
                return True
        return False
                    
    def get_inactive_voices(self) -> list[Voice]:
        """Get all keyboard voices that are "inactive", do not currently have a note assigned. The voices will automatically be sorted by the time they were last assigned a note from oldest to newest.

        :return: all inactive voices
        :rtype: list[:class:`pico_synth_sandbox.keyboard.Voice`]
        """
        voices = [voice for voice in self._voices if not voice.is_active()]
        voices.sort(key=lambda voice: voice.time)
        return voices
    def has_inactive_voices(self) -> bool:
        """Checks to see if any voice is currently "inactive", has not been assigned a note.

        :return: whether or not at least one voice is inactive
        :rtype: bool
        """
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

def get_keyboard_driver(board, max_voices:int=1, root:int=None) -> Keyboard:
    """Automatically generate the proper :class:`pico_synth_sandbox.keyboard.Keyboard` object based on the device's settings.toml configuration.

    :param board: The designated board configuration object. Can be obtained by calling `pico_synth_sandbox.board.get_board()`.
    :type board: :class:`pico_synth_sandbox.board.Board`
    :param max_voices: The maximum number of voices/notes to be played at once.
    :type max_voices: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    :return: a keyboard object for the designated board
    :rtype: :class:`pico_synth_sandbox.keyboard.Keyboard`
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
