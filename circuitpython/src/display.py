class Display:
    def __init__(self):
        self._rs = DigitalInOut(board.GP20)
        self._en = DigitalInOut(board.GP21)
        self._d4 = DigitalInOut(board.GP22)
        self._d5 = DigitalInOut(board.GP26)
        self._d6 = DigitalInOut(board.GP27)
        self._d7 = DigitalInOut(board.GP28)

        self._lcd = Character_LCD_Mono(self._rs, self._en, self._d4, self._d5, self._d6, self._d7, 16, 2)
        self._lcd.cursor = False
        self._lcd.text_direction = self._lcd.LEFT_TO_RIGHT

        self._cursor_enabled = None
        self._cursor_blink = None
        self._cursor_position = (-1,-1)

    def clear(self):
        self._lcd.clear()
        self.set_cursor()

    def write(self, value, position=(0,0), length=None, right_aligned=False):
        if not length:
            length = 16
        if type(value) is float:
            value = "{:.2f}".format(value)
        self._lcd.cursor_position(position[0], position[1])
        self._lcd.message = truncate_str(str(value), length, right_aligned)

    def set_cursor_enabled(self, value):
        if self._cursor_enabled != value:
            self._cursor_enabled = value
            self._lcd.cursor = value
    def set_cursor_position(self, column=0, row=0):
        if self._cursor_position[0] != column or self._cursor_position[1] != row:
            self._cursor_position = (column, row)
            self._lcd.cursor_position(column, row)
    def set_cursor_blink(self, value):
        if self._cursor_blink != value:
            self._cursor_blink = value
            self._lcd.blink = value

    def show_cursor(self, column=0, row=0):
        self.set_cursor_enabled(True)
        self.set_cursor_position(column, row)
    def hide_cursor(self):
        self.set_cursor_disabled(False)
        self.set_cursor(False)
