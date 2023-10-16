class Arpeggiator(Timer):

    NUM_MODES=6
    MODE_UP=0
    MODE_DOWN=1
    MODE_UPDOWN=2
    MODE_DOWNUP=3
    MODE_PLAYED=4
    MODE_RANDOM=5

    def __init__(self, bpm=120, steps=2):
        Timer.__init__(self,
            bpm=bpm,
            steps=steps,
            gate=0.3
        )

        self._raw_notes = []
        self._notes = []

        self.set_mode(os.getenv("ARPEGGIATOR_MODE", 0))
        self._octaves = 0

        self._keyboard = None

    def _reset(self, immediate=True):
        Timer._reset(self, immediate)
        self._pos = 0

    def set_octaves(self, value):
        self._octaves = int(value)
        if self._notes:
            self.update_notes(self._raw_notes)

    def set_keyboard(self, keyboard):
        self._keyboard = keyboard
    def _enable(self):
        if self._keyboard:
            self.update_notes(keyboard.get_notes())
    def _disable(self):
        if self._keyboard:
            self._keyboard.update()

    def get_mode(self):
        return self._mode
    def set_mode(self, value):
        self._mode = value % self.NUM_MODES
        if self._notes: self.update_notes(self._raw_notes)

    def _get_notes(self, notes=[]):
        if not notes: return notes

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
            self._reset()
        self._raw_notes = notes.copy()
        self._notes = self._get_notes(notes)

    def _update(self):
        if self.get_mode() == self.MODE_RANDOM:
            self._pos = random.randrange(0,len(self._notes),1)
        else:
            self._pos = (self._pos+1) % len(self._notes)
        self._do_press(self._notes[self._pos][0], self._notes[self._pos][1])
