class Arpeggiator:
    NUM_MODES=6
    MODE_UP=0
    MODE_DOWN=1
    MODE_UPDOWN=2
    MODE_DOWNUP=3
    MODE_PLAYED=4
    MODE_RANDOM=5

    def __init__(self, bpm=120, steps=2):
        self._enabled = False
        self._gate = 0.3

        self._step_options = [
            0.5, # half
            1.0, # quarter
            1.5, # dotted quarter
            2.0, # eighth
            3.0, # triplet
            4.0, # sixteenth
            8.0  # 32nd
        ]

        self._update_timing(
            bpm=bpm,
            steps=steps
        )

        self._raw_notes = []
        self._notes = []
        self._pos = 0
        self._now = time.monotonic()

        self._press = None
        self._release = None
        self._last_press = 0

        self.set_mode(os.getenv("ARPEGGIATOR_MODE", 0))
        self._octaves = 0

        self._keyboard = None

    def _update_timing(self, bpm=None, steps=None):
        if bpm:
            self._bpm = bpm
        if steps:
            self._steps = steps
        self._step_time = 60.0 / self._bpm / self._steps
        self._gate_duration = self._gate * self._step_time
    def set_bpm(self, value):
        self._update_timing(bpm=value)
    def get_bpm(self):
        return self._bpm
    def set_steps(self, value):
        if type(value) is int:
            value = float(value)
        elif type(value) is dict:
            value = value.get("steps", 1)
        value = max(value, 0.01)
        self._update_timing(steps=value)
    def set_step_option(self, value):
        if not type(value) is int:
            self.set_steps(value)
        else:
            self.set_steps(self._step_options[value % len(self._step_options)])
    def get_steps(self):
        return self._steps
    def get_step_options(self):
        return self._step_options
    def set_gate(self, value):
        self._gate = value
        self._update_timing()
    def set_octaves(self, value):
        self._octaves = int(value)
        if self._notes:
            self.update_notes(self._raw_notes)

    def set_keyboard(self, keyboard):
        self._keyboard = keyboard
    def is_enabled(self):
        return self._enabled
    def set_enabled(self, value, keyboard=None):
        if value:
            self.enable(keyboard)
        else:
            self.disable()
    def toggle(self, keyboard=None):
        self.set_enabled(not self.is_enabled(), keyboard)
    def enable(self, keyboard=None):
        self._enabled = True
        self._now = time.monotonic() - self._step_time
        if keyboard is None and not self._keyboard is None:
            keyboard = self._keyboard
        if keyboard:
            self.update_notes(keyboard.get_notes())
    def disable(self, keyboard=None):
        self._enabled = False
        self.update_notes()
        self._do_release()
        if keyboard is None and not self._keyboard is None:
            keyboard = self._keyboard
        if keyboard:
            keyboard.update()

    def set_press(self, callback):
        self._press = callback
    def set_release(self, callback):
        self._release = callback

    def get_mode(self):
        return self._mode
    def set_mode(self, value):
        self._mode = value % self.NUM_MODES
        if self._notes:
            self.update_notes(self._raw_notes)

    def _get_notes(self, notes=[]):
        if not notes:
            return notes

        if abs(self._octaves) > 0:
            l = len(notes)
            for octave in range(1,abs(self._octaves)+1):
                if self._octaves < 0:
                    octave = octave * -1
                for i in range(0,l):
                    notes.append((notes[i][0] + octave*12, notes[i][1]))

        if self._mode == self.MODE_UP:
            notes.sort(key=lambda x: x[0])
        elif self._mode == self.MODE_DOWN:
            notes.sort(key=lambda x: x[0], reverse=True)
        elif self._mode == self.MODE_UPDOWN:
            notes.sort(key=lambda x: x[0])
            if len(notes) > 2:
                _notes = notes[1:-1].copy()
                _notes.reverse()
                notes = notes + _notes
        elif self._mode == self.MODE_DOWNUP:
            notes.sort(key=lambda x: x[0], reverse=True)
            if len(notes) > 2:
                _notes = notes[1:-1].copy()
                _notes.reverse()
                notes = notes + _notes
        # MODE_PLAYED = notes stay as is, MODE_RANDOM = index is randomized on update

        return notes
    def update_notes(self, notes=[]):
        if not self._notes:
            self._pos = 0
            self._now = time.monotonic() - self._step_time
        self._raw_notes = notes.copy()
        self._notes = self._get_notes(notes)

    def update(self, now=None):
        if not self._enabled or not self._notes:
            return

        if not now:
            now = time.monotonic()

        if now >= self._now + self._step_time:
            self._now = self._now + self._step_time
            if self.get_mode() == self.MODE_RANDOM:
                self._pos = random.randrange(0,len(self._notes),1)
            else:
                self._pos = (self._pos+1) % len(self._notes)
            self._do_press(self._notes[self._pos][0], self._notes[self._pos][1])

        if now - self._now > self._gate_duration:
            self._do_release()

    def _do_press(self, notenum, velocity):
        if self._press:
            self._press(notenum, velocity)
            self._last_press = notenum
    def _do_release(self):
        if self._release and self._last_press > 0:
            self._release(self._last_press)
            self._last_press = 0
