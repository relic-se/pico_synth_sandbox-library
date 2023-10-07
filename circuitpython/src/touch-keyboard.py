class TouchPad(Key):
    def __init__(self, pin):
        self.switch = Debouncer(TouchIn(pin))
    def check(self):
        self.switch.update()
        if self.switch.rose:
            return self.PRESS
        elif self.switch.fell:
            return self.RELEASE
        else:
            return self.NONE

class TouchKeyboard(Keyboard):
    def __init__(self, voices=1):
        Keyboard.__init__(self, [
            TouchPad(board.GP16),
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
        ], 1)
