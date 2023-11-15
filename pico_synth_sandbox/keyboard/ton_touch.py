# pico_synth_sandbox/touch-keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

# NOTE: If using module, close jumpers TP3 & TP4 for multi-key output, TP1 for serial interface (active-high), and TP2 for 16-key inputs (leave open for 8-key).

import board, time
from digitalio import DigitalInOut, Direction, Pull
from pico_synth_sandbox.keyboard import Key, Keyboard

class TonTouchPad(Key):
    def __init__(self, index):
        self._index = index
        self._bit = 1 << self._index

    def check(self):
        # TODO: Some form of debouncing
        global tontouch_data, tontouch_data_prev
        if tontouch_data & self._bit and not tontouch_data_prev & self._bit:
            return self.PRESS
        elif not tontouch_data & self._bit and tontouch_data_prev & self._bit:
            return self.RELEASE
        else:
            return self.NONE

class TonTouchKeyboard(Keyboard):

    MODE_8KEY=0
    MODE_16KEY=1

    def __init__(self, max_notes=1, root=None, input_mode=MODE_16KEY):
        self._input_mode = input_mode
        self._input_bits = (input_mode + 1) * 8
        self._input_delay = 1.0/64.0 # 64hz max refresh rate
        self._input_last = time.monotonic()

        Keyboard.__init__(
            self,
            keys=[TonTouchPad(i) for i in range(self._input_bits)],
            max_notes=max_notes,
            root=root
        )

        self._sdo = DigitalInOut(board.GP6)
        self._sdo.direction = Direction.INPUT
        self._sdo.pull = Pull.UP

        self._scl = DigitalInOut(board.GP7)
        self._scl.direction = Direction.OUTPUT

        global tontouch_data, tontouch_data_prev
        tontouch_data = 0
        tontouch_data_prev = 0

    def update(self):
        if self.read_data():
            Keyboard.update(self)

    def read_data(self):
        now = time.monotonic()
        if now - self._input_last < self._input_delay:
            return False
        self._input_last = now

        global tontouch_data, tontouch_data_prev
        tontouch_data_prev = tontouch_data
        tontouch_data = 0

        # Clock is around 2.8khz
        self._scl.value = True
        for i in range(self._input_bits):
            self._scl.value = False
            if self._sdo.value:
                tontouch_data |= (1 << i)
            self._scl.value = True
        self._scl.value = False

        return True
