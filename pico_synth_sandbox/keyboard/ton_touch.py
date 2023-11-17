# pico_synth_sandbox/touch-keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

# NOTE: If using module, close jumpers TP3 & TP4 for multi-key output, TP1 for serial interface (active-high), and TP2 for 16-key inputs (leave open for 8-key).

import board
from pico_synth_sandbox.keyboard import DebouncerKey, Keyboard
from digitalio import DigitalInOut, Direction, Pull

tontouch_data = 0

class TonTouchPad(DebouncerKey):
    def __init__(self, index):
        self._index = index
        self._bit = 1 << self._index
        DebouncerKey.__init__(self, self.read)

    def read(self):
        global tontouch_data
        return bool(tontouch_data & self._bit)

class TonTouchKeyboard(Keyboard):

    MODE_8KEY  = 0
    MODE_16KEY = 1

    def __init__(self, max_notes=1, root=None, input_mode=MODE_16KEY):
        self._input_mode = input_mode
        self._input_bits = (input_mode + 1) * 8

        Keyboard.__init__(
            self,
            keys=[TonTouchPad(i) for i in range(self._input_bits)],
            max_notes=max_notes,
            root=root
        )
        self.set_update_frequency(64.0) # 64hz max refresh rate

        self._sdo = DigitalInOut(board.GP6)
        self._sdo.direction = Direction.INPUT
        self._sdo.pull = Pull.UP

        self._scl = DigitalInOut(board.GP7)
        self._scl.direction = Direction.OUTPUT

    def update(self):
        self.read_data()
        Keyboard.update(self)

    def read_data(self):
        global tontouch_data
        tontouch_data = 0

        # Clock is around 2.8khz
        self._scl.value = True
        for i in range(self._input_bits):
            self._scl.value = False
            if self._sdo.value:
                tontouch_data |= (1 << i)
            self._scl.value = True
        self._scl.value = False
