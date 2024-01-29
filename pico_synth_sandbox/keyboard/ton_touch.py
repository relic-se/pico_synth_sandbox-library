# pico_synth_sandbox/touch-keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

# NOTE: If using module, close jumpers TP3 & TP4 for multi-key output, TP1 for serial interface (active-high), and TP2 for 16-key inputs (leave open for 8-key).

from pico_synth_sandbox.keyboard import DebouncerKey, Keyboard

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

    def __init__(self, board, max_voices=1, root=None, input_mode=MODE_16KEY, invert_clk=True):
        self._input_mode = input_mode
        self._input_bits = (input_mode + 1) * 8
        self._invert_clk = invert_clk

        Keyboard.__init__(
            self,
            keys=[TonTouchPad(i) for i in range(self._input_bits)],
            max_voices=max_voices,
            root=root
        )
        self.set_update_frequency(64.0) # 64hz max refresh rate

        self._sdo, self._scl = board.get_ttp()
        self._scl.value = self._invert_clk

    def update(self):
        self.read_data()
        Keyboard.update(self)

    def read_data(self):
        global tontouch_data
        tontouch_data = 0

        # Clock is around 2.8khz
        self._scl.value = not self._invert_clk
        for i in range(self._input_bits):
            self._scl.value = self._invert_clk
            if self._sdo.value:
                tontouch_data |= (1 << i)
            self._scl.value = not self._invert_clk
        self._scl.value = self._invert_clk
