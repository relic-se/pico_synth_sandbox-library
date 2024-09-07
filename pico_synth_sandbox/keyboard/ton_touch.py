# pico_synth_sandbox/touch-keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

# NOTE: If using module, close jumpers TP3 & TP4 for multi-key output, TP1 for serial interface (active-high), and TP2 for 16-key inputs (leave open for 8-key).

from pico_synth_sandbox.keyboard import DebouncerKey, Keyboard
import array

tontouch_data = array.array('H', [0])

class TonTouchPad(DebouncerKey):
    def __init__(self, index):
        self._index = index
        self._bit = 1 << self._index
        DebouncerKey.__init__(self, self.read)

    def read(self):
        global tontouch_data
        return bool(tontouch_data[0] & self._bit)

class TonTouchKeyboard(Keyboard):

    MODE_8KEY  = 0
    MODE_16KEY = 1

    def __init__(self, board, max_voices=1, root=None, input_mode=MODE_16KEY, invert_clk=True):
        import rp2pio
        import adafruit_pioasm
        
        self._input_mode = input_mode
        self._input_bits = (input_mode + 1) * 8
        #self._invert_clk = invert_clk

        Keyboard.__init__(
            self,
            keys=[TonTouchPad(i) for i in range(self._input_bits)],
            max_voices=max_voices,
            root=root
        )

        clk_off = 1 if invert_clk else 0
        clk_on = 0 if invert_clk else 0
        clk_cnt = self._input_bits - 1
        pioasm = f"""
.program read_ttp
    set pins, {clk_off}
.wrap_target
    set y, 3
tout_y:
    set x, 31
tout_x:
    nop [31]
    jmp x-- tout_x
    jmp y-- tout_y
    set x, {clk_cnt}
bitloop:
    set pins, {clk_on} [3]
    set pins, {clk_off} [1]
    in pins, 1
    jmp x-- bitloop
    push
.wrap
"""
        self._piosm = rp2pio.StateMachine(
            adafruit_pioasm.assemble(pioasm),
            frequency=2000000, # 2MHz, cycle = 0.5us
            first_in_pin=board.ttp_sdo,
            in_pin_count=1,
            pull_in_pin_up=1,
            first_set_pin=board.ttp_scl,
            set_pin_count=1,
            initial_set_pin_state=clk_off,
            initial_set_pin_direction=1,
        )
        # Timing Details:
        # Clock Cycle (F_SCL) = 8 pio cycles = 4us = 250KHz
        # Word Cycle = 64us = ~15.6KHz
        # Delay (Tout) = 2ms
        # Frequency (T_resp) = 2064us = ~484.5Hz
        self.set_update_frequency(484)

    async def update(self):
        self.read_data()
        await Keyboard.update(self)

    def read_data(self):
        global tontouch_data
        if self._piosm.in_waiting <= 0: return
        self._piosm.readinto(tontouch_data)
