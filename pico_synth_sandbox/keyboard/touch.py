# pico_synth_sandbox/touch-keyboard.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

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
    """Use direct capactivie touch GPIO inputs as a :class:`pico_synth_sandbox.keyboard.Keyboard` object. GPIO pins and order are defined by `board.get_touch_keys()`.

    :param board: The designated board configuration object. Can be obtained by calling `pico_synth_sandbox.board.get_board()`.
    :type board: :class:`pico_synth_sandbox.board.Board`
    :param max_voices: The maximum number of voices/notes to be played at once.
    :type max_voices: int
    :param root: Set the base note number of the physical key inputs. If left as `None`, the `KEYBOARD_ROOT` settings.toml value will be used instead.
    :type root: int
    """
    def __init__(self, board, max_voices:int=1, root:int=None):
        keys = []
        for pin in board.get_touch_keys():
            keys.append(TouchPad(pin))
        Keyboard.__init__(self, keys, max_voices, root)
