class Sequencer(Timer):
    """Sequence notes using the :class:`pico_synth_sandbox.Timer` class to create a multi-track sixteenth note sequencer. By default, the Sequencer is set up for a single 4/4 measure of 16 notes with one track. Each note of each track can be assigned any note value and velocity. The length and number of tracks can be reassigned during runtime.

    :param length: The number of sixteenth note steps of each track. The minimum value allowed is 1.
    :type length: int
    :param tracks: The number of tracks to create and sequence. The minimum value allowed is 1.
    :type tracks: int
    :param bpm: The beats per minute of timer.
    :type bpm: int
    """
    def __init__(self, length=16, tracks=1, bpm=120):
        Timer.__init__(self,
            bpm=bpm,
            steps=Timer.STEP_SIXTEENTH
        )

        self._length = max(length, 1)
        self._tracks = max(tracks, 1)
        self._data = [[None for j in range(self._length)] for i in range(self._tracks)]
        self._pos = 0

    def set_length(self, value):
        """Set the number of sixteenth notes for each track. If the length is shortened, all of the step data beyond the new length will be deleted, and if the sequencer is also currently running, it should loop back around automatically to the start of the track data.

        :param value: The number of sixteenth note steps of each track. The minimum value allowed is 1.
        :type value: int
        """
        value = max(value, 1)
        if value > self._length:
            for i in range(self._tracks):
                self._data[i] = self._data[i] + [None for j in range(value - self._length)]
        elif value < self._length:
            for i in range(self._tracks):
                del self._data[i][value:]
        self._length = value
    def get_length(self):
        """Get the number of sixteenth notes for each track.

        :return: track length
        :rtype: int
        """
        return self._length

    def set_tracks(self, value):
        """Set the number of note tracks to sequence. If the number of tracks is shortened, the tracks at an index greater to or equal than the number will be deleted. If a larger number of tracks is provided, the newly created tracks will be empty.

        :param value: The number of tracks to sequence. The minimum value allowed is 1.
        :type value: int
        """
        value = max(value, 1)
        if value > self._tracks:
            self._data = self._data + [[None for j in range(self._length)] for i in range(value - self._tracks)]
        elif value < self._tracks:
            del self._data[value:]
        self._tracks = value
    def get_tracks(self):
        """Get the number tracks being sequenced.

        :return: track count
        :rtype: int
        """
        return self._tracks

    def get_position(self):
        """Get the current position of the sequencer within the track length (0-based).

        :return: sequencer position
        :rtype: int
        """
        return self._pos

    def set_note(self, position, notenum, velocity=1.0, track=0):
        """Set the note value and velocity of a track at a specific step index.

        :param position: Index of the step (0-based). Will be limited to the track length.
        :type position: int
        :param notenum: Value of the note.
        :type notenum: int
        :param velocity: Velocity of the note (0.0-1.0).
        :type velocity: float
        :param track: Index of the track (0-based). Will be limited to the track count.
        :type track: int
        """
        track = clamp(track, 0, self._tracks)
        position = clamp(position, 0, self._length)
        self._data[track][position] = (notenum, velocity)
    def get_note(self, position, track=0):
        """Get the note data for a specified track and step position. If a note isn't defined at specific index, a value of `None` will be returned.

        :param position: Index of the step (0-based). Will be limited to the track length.
        :type position: int
        :param track: Index of the track (0-based). Will be limited to the track count.
        :type track: int
        :return: note data (notenum, velocity)
        :rtype: tuple
        """
        track = clamp(track, 0, self._tracks)
        position = clamp(position, 0, self._length)
        return self._data[track][position]
    def has_note(self, position, track=0):
        """Check whether or note a specific step within a track has been set with note data.

        :param position: Index of the step (0-based). Will be limited to the track length.
        :type position: int
        :param track: Index of the track (0-based). Will be limited to the track count.
        :type track: int
        :return: if the track step has a note
        :rtype: bool
        """
        return not self.get_note(position, track) is None
    def remove_note(self, position, track=0):
        """Remove the note data as a specific step within a track.

        :param position: Index of the step (0-based). Will be limited to the track length.
        :type position: int
        :param track: Index of the track (0-based). Will be limited to the track count.
        :type track: int
        """
        track = clamp(track, 0, self._tracks)
        position = clamp(position, 0, self._length)
        self._data[track][position] = None

    def get_track(self, track=0):
        """Get list of note data for a specified track index (0-based). If the track isn't available, a value of `None` will be returned.

        :return: track data list of note tuples as (notenum, velocity)
        :rtype: list
        """
        if track < 0 or track >= self._tracks: return None
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
