# pico_synth_sandbox/arpeggiator.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import random
from pico_synth_sandbox import clamp
from pico_synth_sandbox.timer import Timer
from pico_synth_sandbox.keyboard import Note

class Arpeggiator(Timer):

    NUM_MODES   = 6
    MODE_UP     = 0
    MODE_DOWN   = 1
    MODE_UPDOWN = 2
    MODE_DOWNUP = 3
    MODE_PLAYED = 4
    MODE_RANDOM = 5

    def __init__(self, bpm=120, steps=2.0, mode=0, octaves=0, probability=1.0):
        Timer.__init__(self,
            bpm=bpm,
            steps=steps,
            gate=0.3
        )

        self._raw_notes = []
        self._notes = []

        self.set_mode(mode)
        self.set_octaves(octaves)
        self._probability = probability

        self._keyboard = None

    def _reset(self, immediate=True):
        Timer._reset(self, immediate)
        self._pos = 0

    def get_octaves(self):
        return self._octaves
    def set_octaves(self, value):
        self._octaves = int(value)
        if self._notes:
            self.update_notes(self._raw_notes)

    def get_probability(self):
        return self._probability
    def set_probability(self, value):
        self._probability = clamp(value, 0.0, 1.0)

    def set_keyboard(self, keyboard):
        self._keyboard = keyboard
    def _enable(self):
        if self._keyboard:
            self.update_notes(self._keyboard.get_notes())
    def _disable(self):
        if self._keyboard:
            self._keyboard.force_update()

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
                    notes.append(Note(notes[i].notenum + octave*12, notes[i].velocity))

        if self._mode == self.MODE_UP:
            notes.sort()
        elif self._mode == self.MODE_DOWN:
            notes.sort(reverse=True)
        elif self._mode == self.MODE_UPDOWN:
            notes.sort()
            if len(notes) > 2:
                _notes = notes[1:-1].copy()
                _notes.reverse()
                notes = notes + _notes
        elif self._mode == self.MODE_DOWNUP:
            notes.sort(reverse=True)
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
        if self._notes:
            if self._probability < 1.0 and (self._probability == 0.0 or random.random() > self._probability):
                return
            if self.get_mode() == self.MODE_RANDOM:
                self._pos = random.randrange(0,len(self._notes),1)
            else:
                self._pos = (self._pos+1) % len(self._notes)
            self._do_press(self._notes[self._pos].notenum, self._notes[self._pos].velocity)
