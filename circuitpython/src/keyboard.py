# TODO: Add Output Buffer Voices

class Key:
    NONE=0
    PRESS=1
    RELEASE=2
    def __init__(self):
        pass
    def check(self):
        return self.NONE

class Keyboard:
    NUM_MODES=3
    MODE_HIGH=0
    MODE_LOW=1
    MODE_LAST=2

    def __init__(self, keys=[], voices=1):
        self.root = os.getenv("KEYBOARD_ROOT", 36)
        self.keys = keys
        self.voices = voices # Not implemented

        self._notes = []
        self._sustain = False
        self._sustained = []
        self._press = None
        self._release = None
        self._arpeggiator = None

        self.set_mode(os.getenv("KEYBOARD_MODE", self.MODE_HIGH))

    def set_press(self, callback):
        self._press = callback
        if self._arpeggiator:
            self._arpeggiator.set_press(callback)
    def set_release(self, callback):
        self._release = callback
        if self._arpeggiator:
            self._arpeggiator.set_release(callback)
    def set_arpeggiator(self, arpeggiator):
        self._arpeggiator = arpeggiator
        self._arpeggiator.set_keyboard(self)
        if self._press:
            self._arpeggiator.set_press(self._press)
        if self._release:
            self._arpeggiator.set_release(self._release)

    def get_mode(self):
        return self._mode
    def set_mode(self, value):
        self._mode = value % self.NUM_MODES

    def get_sustain(self):
        return self._sustain
    def set_sustain(self, value, update=True):
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
        if include_sustained and self._sustain and self._sustained:
            return True
        if self._notes:
            return True
        return False
    def get_notes(self, include_sustained=True):
        if not self.has_notes(include_sustained):
            return []
        if include_sustained:
            return (self._notes if self._notes else []) + (self._sustained if self._sustain and self._sustained else [])
        else:
            return self._notes

    def has_note(self, notenum, include_sustained=True):
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
        if self._mode == self.MODE_HIGH:
            return self._get_high()
        elif self._mode == self.MODE_LOW:
            return self._get_low()
        else: # self.MODE_LAST
            return self._get_last()

    def append(self, notenum, velocity, keynum=None, update=True):
        self.remove(notenum, None, False, True)
        note = (notenum, velocity, keynum)
        self._notes.append(note)
        if self._sustain:
            self._sustained.append(note)
        if update:
            self._update()
    def remove(self, notenum, keynum=None, update=True, remove_sustained=False):
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
        if self.keys:
            for i in range(len(self.keys)):
                j = self.keys[i].check()
                if j == Key.PRESS:
                    self.append(self.root + i, 127, i) # Velocity is hard-coded
                elif j == Key.RELEASE:
                    self.remove(self.root + i, i)

        if self._arpeggiator:
            self._arpeggiator.update()

    def _update(self):
        if not self._arpeggiator or not self._arpeggiator.is_enabled():
            note = self.get()
            if note and self._press:
                self._press(note[0], note[1], note[2])
        elif self.has_notes():
            self._arpeggiator.update_notes(self.get_notes())
        else:
            self._arpeggiator.update_notes()
