# pico_synth_sandbox/display.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import clamp, truncate_str, unmap_value
import math
import board
from digitalio import DigitalInOut
from adafruit_character_lcd.character_lcd import Character_LCD_Mono

class Display:
    """Control the connected 16x2 character display (aka *1602*). Hardware connections are abstracted and text writing and cursor management is simplified.
    """

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
        """Remove all text from display and hide and reset cursor position
        """
        self._lcd.clear()
        self.set_cursor_enabled(False)
        self.set_cursor_position(0, 0, True)

    def write(self, value, position=(0,0), length=None, right_aligned=False, reset_cursor=True):
        """Display a string or number on the display at the designated position. Can be truncated to a specified length and right-aligned.

        :param value: The message or number you would like to display. Any part of the string beyond the first 16 characters or the defined length will not be displayed.
        :type value: string, float
        :param position: Use a tuple of two 0-based integers for the column and row of that you would like to write the value to. Ie: (x,y). The column (x) should be between 0 and 15 and the row (y) should be between 0 and 1.
        :type position: tuple
        :param length: The length of the message you would like to write. By default, the length will be 16 or the length to the last column of the row from the designated x-position.
        :type length: int
        :param right_aligned: Whether or not you would like to align the data to the right padded by spaces as determined by the designated length.
        :type right_align: bool
        :param reset_cursor: It is required to manipulate the cursor position in order to make writes to the display. By default, the cursor is reset to the previous position if needed for other applications. If you would like to keep the cursor at it's newly written location, set this value as False.
        :type reset_cursor: bool
        """
        if not length: length = 16
        if type(value) is float:
            value = "{:.2f}".format(value)

        cursor_pos = self._cursor_position
        self.set_cursor_position(position[0], position[1], True)
        self._lcd.message = truncate_str(str(value), clamp(length,1,16-self._cursor_position[0]), right_aligned)
        if reset_cursor: self.set_cursor_position(cursor_pos[0], cursor_pos[1])

    def set_cursor_enabled(self, value):
        """Set whether or not the cursor should be displayed.

        :param value: The visibility of the cursor.
        :type value: bool
        """
        if self._cursor_enabled != value:
            self._cursor_enabled = value
            self._lcd.cursor = value
    def set_cursor_position(self, column=0, row=0, force=False):
        """Set the position of the cursor.

        :param column: The x-position or column of the cursor which should be between 0 and 15.
        :type column: int
        :param row: The y-position or row of the cursor which should be between 0 and 1.
        :type row: int
        :param force: Force the display to update the cursor position even if it hasn't changed.
        :type force: bool
        """
        column = clamp(column, 0, 15)
        row = clamp(row, 0, 1)
        if force or self._cursor_position[0] != column or self._cursor_position[1] != row:
            self._cursor_position = (column, row)
            self._lcd.cursor_position(column, row)
    def set_cursor_blink(self, value):
        """Set whether or not the cursor should blink.

        :param value: The blinking state of the cursor.
        :type value: bool
        """
        if self._cursor_blink != value:
            self._cursor_blink = value
            self._lcd.blink = value

    def show_cursor(self, column=0, row=0):
        """A quick method to ensure that the cursor is being displayed and set the position. Will not cause unnecessary display writes if called multiple times.

        :param column: The x-position or column of the cursor which should be between 0 and 15.
        :type column: int
        :param row: The y-position or row of the cursor which should be between 0 and 1.
        :type row: int
        """
        self.set_cursor_enabled(True)
        self.set_cursor_position(column, row)
    def hide_cursor(self):
        """A quick method to hide the cursor.
        """
        self.set_cursor_enabled(False)

    def enable_vertical_graph(self):
        data = []
        for i in range(1, 8):
            data.append([0x00 for i in range(8-i)] + [0x1f for i in range(i)])
        self.load_character_data(data)
    def enable_horizontal_graph(self):
        data = []
        for i in range(1, 5):
            val = 0x00
            for j in range(i):
                val |= (1<<(4-j))
            data.append([val for j in range(8)])
        self.load_character_data(data)
    def load_character_data(self, data):
        for i in range(min(len(data), 8)):
            self._lcd.create_char(i, data[i])

    def _write_graph(self, value=0.0, minimum=0.0, maximum=1.0, position=(0,0), length=1, vertical=False, reset_cursor=True):
        if reset_cursor: cursor_pos = self._cursor_position

        length = clamp(length, 1, (2 if vertical else 16) - position[1 if vertical else 0])
        value = unmap_value(value, minimum, maximum)

        segment = 1.0 / length
        bar = segment / (9.0 if vertical else 6.0)

        data = []
        for i in range(length):
            if value >= segment*(i+1)-bar:
                char = 0xff
            elif value <= segment*i+bar:
                char = 0xfe
            else:
                char = 0x00 + int(math.floor((value - (segment*i+bar)) / bar))
            data.append(chr(char))

        if vertical:
            for i in range(length):
                self.set_cursor_position(position[0], position[1]+(length-i-1), True)
                self._lcd.message = data[i]
        else:
            self.set_cursor_position(position[0], position[1], True)
            self._lcd.message = "".join(data)

        if reset_cursor: self.set_cursor_position(cursor_pos[0], cursor_pos[1])

    def write_vertical_graph(self, value=0.0, minimum=0.0, maximum=1.0, position=(0,0), height=1, reset_cursor=True):
        self._write_graph(value, minimum, maximum, position, height, True, reset_cursor)

    def write_horizontal_graph(self, value=0.0, minimum=0.0, maximum=1.0, position=(0,0), width=1, reset_cursor=True):
        self._write_graph(value, minimum, maximum, position, width, False, reset_cursor)
