class Sequencer(Timer):
    def __init__(self, length=16, tracks=1, bpm=120):
        Timer.__init__(self,
            bpm=bpm,
            steps=Timer.STEP_SIXTEENTH
        )

        self._length = max(length, 1)
        self._tracks = max(tracks, 1)
        self._data = [[None for j in range(self._length)] for i in range(self._tracks)]
        self._pos = 0

    def set_length(self, length):
        length = max(length, 1)
        if length > self._length:
            for i in range(self._tracks):
                self._data[i] = self._data[i] + [None for j in range(length - self._length)]
        elif length < self._length:
            for i in range(self._tracks):
                del self._data[i][length:]
        self._length = length
    def get_length(self):
        return self._length

    def set_tracks(self, tracks):
        tracks = max(tracks, 1)
        if tracks > self._tracks:
            self._data = self._data + [[None for j in range(self._length)] for i in range(tracks - self._tracks)]
        elif tracks < self._tracks:
            del self._data[tracks:]
        self._tracks = tracks
    def get_tracks(self):
        return self._tracks

    def get_position(self):
        return self._pos

    def set_note(self, position, notenum, velocity=1.0, track=0):
        track = clamp(track, 0, self._tracks)
        position = clamp(position, 0, self._length)
        self._data[track][position] = (notenum, velocity)
    def get_note(self, position, track=0):
        track = clamp(track, 0, self._tracks)
        position = clamp(position, 0, self._length)
        return self._data[track][position]
    def has_note(self, position, track=0):
        return not self.get_note(position, track) is None
    def remove_note(self, position, track=0):
        track = clamp(track, 0, self._tracks)
        position = clamp(position, 0, self._length)
        self._data[track][position] = None

    def get_track(self, track=0):
        track = clamp(track, 0, self._tracks)
        return self._data[track]

    def _update(self):
        self._pos = (self._pos+1) % self._length
        for i in range(self._tracks):
            note = self._data[i][self._pos]
            if note and note[0] > 0 and note[1] > 0:
                self._do_press(note[0], note[1])

    def _do_step(self):
        if self._step:
            self._step(self._pos)
