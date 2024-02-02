# pico_synth_sandbox/display.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox.tasks import Task
from pico_synth_sandbox import clamp, truncate_str, unmap_value
import math
from digitalio import DigitalInOut
from adafruit_character_lcd.character_lcd import Character_LCD_Mono

class Display(Task):
    """Control the connected 16x2 character display (aka *1602*). Hardware connections are abstracted and text writing and cursor management is simplified.
    """

    def __init__(self, board):
        self._lcd = board.get_lcd()
        self._lcd.cursor = False
        self._lcd.text_direction = self._lcd.LEFT_TO_RIGHT

        self._cursor_enabled = None
        self._cursor_blink = None
        self._cursor_position = (-1,-1)

        self._buffer = [
            [['\0' for x in range(16)] for y in range(2)], # Input Buffer
            [[' ' for x in range(16)] for y in range(2)] # Output Buffer
        ]
        self._needs_update = False

        Task.__init__(self, update_frequency=4)

    def clear(self):
        """Remove all text from display and hide and reset cursor position
        """
        self._lcd.clear()
        self.set_cursor_enabled(False)
        self.set_cursor_position(0, 0, True)
        for y in range(2):
            for x in range(16):
                self._buffer[0][y][x] = '\0'
                self._buffer[1][y][x] = ' '
        self._needs_update = False

    def write(self, value, position=(0,0), length=None, right_aligned=False):
        """Display a string or number on the display at the designated position. Can be truncated to a specified length and right-aligned.

        :param value: The message or number you would like to display. Any part of the string beyond the first 16 characters or the defined length will not be displayed.
        :type value: string, float
        :param position: Use a tuple of two 0-based integers for the column and row of that you would like to write the value to. Ie: (x,y). The column (x) should be between 0 and 15 and the row (y) should be between 0 and 1.
        :type position: tuple
        :param length: The length of the message you would like to write. By default, the length will be 16 or the length to the last column of the row from the designated x-position.
        :type length: int
        :param right_aligned: Whether or not you would like to align the data to the right padded by spaces as determined by the designated length.
        :type right_align: bool
        """
        position = self._sanitize_position(position)
        if not length: length = 16
        length = clamp(length,1,16-position[0])
        if type(value) is float:
            value = "{:.2f}".format(value)
        value = truncate_str(str(value), length, right_aligned)
        for x in range(length):
            self._buffer[0][position[1]][position[0]+x] = value[x]
        self._needs_update = True

    async def update(self, reset_cursor=True):
        """Write buffer to display. Must be called after any changes are made to the display for those changes to be visible.

        :param reset_cursor: It is required to manipulate the cursor position in order to make writes to the display. By default, the cursor is reset to the previous position if needed for other applications. If you would like to keep the cursor at it's newly written location, set this value as False.
        :type reset_cursor: bool
        """

        # Exit early if no buffer updates recorded
        if not self._needs_update:
            return

        # Locate the end of front buffer data
        end = -1
        for i in range(2*16-1, -1, -1):
            x = i % 16
            y = i // 16
            if self._buffer[0][y][x] != '\0' and self._buffer[0][y][x] != self._buffer[1][y][x]:
                end = i
                break
        if end < 0:
            return # No changes found
        
        # Locate the start of front buffer data and start building data
        start = -1
        data = []
        for i in range(2*16):
            x = i % 16
            y = i // 16
            if start < 0:
                if self._buffer[0][y][x] != '\0' and self._buffer[0][y][x] != self._buffer[1][y][x]:
                    start = i
                    if start-end+1 == 2*16: # Needs full buffer refresh
                        break
                else:
                    continue
            if self._buffer[0][y][x] != '\0':
                self._buffer[1][y][x] = self._buffer[0][y][x]
            data.append(self._buffer[1][y][x])
            if i == end: # We've reached the end of new buffer data
                break
            elif x == 15: # We're at the end of a line
                data.append('\n')

        if not data: # If no data appended, needs full buffer refresh
            data = "\n".join(["".join(self._buffer[1][y]) for y in range(2)])
        else:
            data = "".join(data)
        
        # Write new data to display
        self._lcd.cursor_position(start%16, start//16)
        self._lcd.message = data
        if reset_cursor:
            self._lcd.cursor_position(self._cursor_position[0], self._cursor_position[1])
        
        # Reset input buffer
        for y in range(2):
            for x in range(16):
                self._buffer[0][y][x] = '\0'

    def _sanitize_position(self, column, row=0):
        if type(column) is tuple:
            if len(column) != 2:
                return (0,0)
            row = column[1]
            column = column[0]
        return (clamp(column, 0, 15), clamp(row, 0, 1))

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

        :param column: The x-position or column of the cursor which should be between 0 and 15. Can use a tuple of (x,y) to set both column and row.
        :type column: int|tuple
        :param row: The y-position or row of the cursor which should be between 0 and 1.
        :type row: int
        :param force: Force the display to update the cursor position even if it hasn't changed.
        :type force: bool
        """
        column, row = self._sanitize_position(column, row)
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
        # Left to Right
        for i in range(1, 5):
            val = 0x00
            for j in range(i):
                val |= (1<<(4-j))
            data.append([val for j in range(8)])
        # Right to Left
        for i in range(1, 5):
            val = 0x00
            for j in range(i):
                val |= (1<<j)
            data.append([val for j in range(8)])
        self.load_character_data(data)
    def load_character_data(self, data):
        for i in range(min(len(data), 8)):
            self._lcd.create_char(i, data[i])

    def _write_graph(self, value=0.0, minimum=0.0, maximum=1.0, position=(0,0), length=1, vertical=False, centered=False):
        position = self._sanitize_position(position)
        length = clamp(length, 1, (2 if vertical else 16) - position[1 if vertical else 0])
        value = unmap_value(value, minimum, maximum)

        segment = 1.0 / length
        bar = segment / (9.0 if vertical else 6.0)

        data = []
        start = 0
        if not vertical and centered:
            start = length//2
            for i in range(0, start):
                if value <= segment*i+bar:
                    char = 0xff
                elif value >= segment*(i+1)-bar:
                    char = 0xfe
                else:
                    char = 0x07 - int(math.floor((value - (segment*i+bar)) / bar))
                data.append(chr(char))
        for i in range(start, length):
            if value >= segment*(i+1)-bar:
                char = 0xff
            elif value <= segment*i+bar:
                char = 0xfe
            else:
                char = 0x00 + int(math.floor((value - (segment*i+bar)) / bar))
            data.append(chr(char))

        for i in range(length):
            if vertical:
                self._buffer[0][position[1]+(length-i-1)][position[0]] = data[i]
            else:
                self._buffer[0][position[1]][position[0]+i] = data[i]
        self._needs_update = True

    def write_vertical_graph(self, value=0.0, minimum=0.0, maximum=1.0, position=(0,0), height=1):
        self._write_graph(value, minimum, maximum, position, height, True, False)

    def write_horizontal_graph(self, value=0.0, minimum=0.0, maximum=1.0, position=(0,0), width=1, centered=False):
        # NOTE: If horizontal centered, length must be divisible by 2.
        self._write_graph(value, minimum, maximum, position, width, False, centered)
