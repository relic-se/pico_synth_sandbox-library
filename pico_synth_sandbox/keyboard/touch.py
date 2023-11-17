# pico_synth_sandbox/touch-keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import board
from pico_synth_sandbox.keyboard import DebouncerKey, Keyboard
from touchio import TouchIn

class TouchPad(DebouncerKey):
    """This class is used by the :class:`pico_synth_sandbox.keyboard.touch.TouchKeyboard` class to handle logic related to the capacitive touch inputs of the hardware platform.

    :param pin: The GPIO pin of the capacitive touch input. Must use a pull-down resistor of around 1M ohms.
    :type pin: :class:`microcontroller.Pin`
    """
    def __init__(self, pin):
        DebouncerKey.__init__(self, TouchIn(pin))

class TouchKeyboard(Keyboard):
    """Use the built-in 12 capacitive touch inputs as a :class:`pico_synth_sandbox.keyboard.Keyboard` object.

    :param max_notes: The maximum number of notes to be played at once. Currently, this feature is not implemented. When using the `get` method, the result is monophonic (1 note).
    :type max_notes: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    """
    def __init__(self, max_notes=1, root=None):
        Keyboard.__init__(self, [
            TouchPad(board.GP19),
            TouchPad(board.GP3),
            TouchPad(board.GP6),
            TouchPad(board.GP7),
            TouchPad(board.GP8),
            TouchPad(board.GP9),
            TouchPad(board.GP10),
            TouchPad(board.GP11),
            TouchPad(board.GP12),
            TouchPad(board.GP13),
            TouchPad(board.GP14),
            TouchPad(board.GP15)
        ], max_notes, root)
