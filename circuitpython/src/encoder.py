class Encoder:

    def __init__(self):
        self._encoder = IncrementalEncoder(board.GP1, board.GP0)
        self._position = None

        self._button_pin = DigitalInOut(board.GP2)
        self._button_pin.direction = Direction.INPUT
        self._button_pin.pull = Pull.UP
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

    def set_increment(self, callback):
        self._increment = callback
    def set_decrement(self, callback):
        self._decrement = callback
    def set_click(self, callback):
        self._click = callback
    def set_double_click(self, callback):
        self._double_click = callback
    def set_long_press(self, callback):
        self._long_press = callback

    def update(self):
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