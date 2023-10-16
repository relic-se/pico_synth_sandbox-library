class Timer:

    STEP_HALF = 0.5
    STEP_QUARTER = 1.0
    STEP_DOTTED_QUARTER = 1.5
    STEP_EIGHTH = 2.0
    STEP_TRIPLET = 3.0
    STEP_SIXTEENTH = 4.0
    STEP_THIRTYSECOND = 8.0
    STEPS = [
        STEP_HALF,
        STEP_QUARTER,
        STEP_DOTTED_QUARTER,
        STEP_EIGHTH,
        STEP_TRIPLET,
        STEP_SIXTEENTH,
        STEP_THIRTYSECOND
    ]

    def __init__(self, bpm=120, steps=2, gate=0.5):
        self._enabled = False
        self._gate = clamp(gate)

        self._reset(False)
        self._update_timing(
            bpm=bpm,
            steps=max(float(steps), 0.25)
        )

        self._step = None
        self._press = None
        self._release = None
        self._last_press = []

    def _update_timing(self, bpm=None, steps=None):
        if bpm: self._bpm = bpm
        if steps: self._steps = steps
        self._step_time = 60.0 / self._bpm / self._steps
        self._gate_duration = self._gate * self._step_time

    def _reset(self, immediate=True):
        self._now = time.monotonic()
        if immediate:
            self._now -= self._step_time

    def set_bpm(self, value):
        self._update_timing(bpm=value)
    def get_bpm(self):
        return self._bpm
    
    def set_steps(self, value):
        value = max(float(value), 0.01)
        self._update_timing(steps=value)
    def get_steps(self):
        return self._steps
    
    def set_gate(self, value):
        self._gate = clamp(value)
        self._update_timing()
    def get_gate(self):
        return self._gate

    def is_enabled(self):
        return self._enabled
    def enable(self):
        self._enabled = True
        self._now = time.monotonic() - self._step_time
        self._enable()
    def _enable(self):
        pass
    def disable(self, keyboard=None):
        self._enabled = False
        self._do_release()
        self._disable()
    def _disable(self):
        pass
    def toggle(self):
        if self.is_enabled():
            self.disable()
        else:
            self.enable()

    def set_step(self, callback):
        self._step = callback
    def set_press(self, callback):
        self._press = callback
    def set_release(self, callback):
        self._release = callback

    def _is_active(self):
        return self._enabled

    def update(self):
        if not self._is_active(): return
        now = time.monotonic()

        if now >= self._now + self._step_time:
            self._now = self._now + self._step_time
            self._update()
            self._do_step()

        if now - self._now > self._gate_duration:
            self._do_release()
    def _update(self):
        pass

    def _do_step(self):
        if self._step:
            self._step()
    def _do_press(self, notenum, velocity):
        if self._press:
            self._press(notenum, velocity)
            self._last_press.append(notenum)
    def _do_release(self):
        if self._release and self._last_press:
            for notenum in self._last_press:
                self._release(notenum)
            self._last_press.clear()
