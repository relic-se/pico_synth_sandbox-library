# pico_synth_sandbox/encoder.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox.tasks import Task
from digitalio import DigitalInOut, Direction, Pull
from rotaryio import IncrementalEncoder
from adafruit_debouncer import Button

class Encoder(Task):
    """Use the on-board encoder to control your program with simple function callbacks. Supports increment, decrement, click, double click, and long press actions.
    """

    def __init__(self, board, index=0):
        self._encoder, self._button_pin = board.get_encoder(index)
        self._position = None
        self._button = Button(
            self._button_pin,
            short_duration_ms=200,
            long_duration_ms=500,
            value_when_pressed=False
        )

        self._increment = None
        self._decrement = None
        self._click = None
        self._double_click = None
        self._long_press = None

        Task.__init__(self, update_frequency=150)

    def set_increment(self, callback):
        """Set the callback method you would like to be called when the encoder is incremented (turned right).

        :param callback: The callback method. No callback parameters are defined.
        :type callback: function
        """
        self._increment = callback
    def set_decrement(self, callback):
        """Set the callback method you would like to be called when the encoder is decremented (turned left).

        :param callback: The callback method. No callback parameters are defined.
        :type callback: function
        """
        self._decrement = callback
    def set_click(self, callback):
        """Set the callback method you would like to be called when the encoder is pressed with a short click (at least 200ms).

        :param callback: The callback method. No callback parameters are defined.
        :type callback: function
        """
        self._click = callback
    def set_double_click(self, callback):
        """Set the callback method you would like to be called when the encoder is pressed with two short clicks.

        :param callback: The callback method. No callback parameters are defined.
        :type callback: function
        """
        self._double_click = callback
    def set_long_press(self, callback):
        """Set the callback method you would like to be called when the encoder is pressed with a single long press (at least 500ms).

        :param callback: The callback method. No callback parameters are defined.
        :type callback: function
        """
        self._long_press = callback

    async def update(self):
        """Update the encoder logic and call any pre-defined callbacks if triggered.
        """
        position = self._encoder.position
        if not self._position is None and position != self._position:
            p = position
            if position > self._position and self._increment:
                while p > self._position:
                    p=p-1
                    self._increment()
            elif position < self._position and self._decrement:
                while p < self._position:
                    p=p+1
                    self._decrement()
        self._position = position

        self._button.update()
        if self._button.long_press and self._long_press:
            self._long_press()
        if self._button.short_count > 0:
            if self._double_click and self._button.short_count >= 2:
                self._double_click()
            elif self._click:
                self._click()
