class Midi:

    def __init__(self):
        self._thru = False
        self._note_on = None
        self._note_off = None
        self._control_change = None
        self._pitch_bend = None
        self._program_change = None

        if os.getenv("MIDI_UART", 0) > 0:
            self._uart = UART(
                tx=board.GP4,
                rx=board.GP5,
                baudrate=31250,
                timeout=0.001
            )
            self._uart_midi = adafruit_midi.MIDI(
                midi_in=self._uart,
                midi_out=self._uart,
                in_channel=os.getenv("MIDI_CHANNEL", 0),
                out_channel=os.getenv("MIDI_CHANNEL", 0),
                debug=False
            )
        else:
            self._uart_midi = None

        if os.getenv("MIDI_USB", 0) > 0:
            self._usb_midi = adafruit_midi.MIDI(
                midi_in=usb_midi.ports[0],
                midi_out=usb_midi.ports[1],
                in_channel=os.getenv("MIDI_CHANNEL", 0),
                out_channel=os.getenv("MIDI_CHANNEL", 0),
                debug=False
            )
        else:
            self._usb_midi = None

        self._led = DigitalInOut(board.LED)
        self._led.direction = Direction.OUTPUT
        self._led.value = False
        self._led_duration = 0.01
        self._led_last = time.monotonic()

    def set_note_on(self, callback):
        self._note_on = callback
    def set_note_off(self, callback):
        self._note_off = callback
    def set_control_change(self, callback):
        self._control_change = callback
    def set_pitch_bend(self, callback):
        self._pitch_bend = callback
    def set_program_change(self, callback):
        self._program_change = callback

    def set_channel(self, value):
        if self._uart_midi:
            self._uart_midi.in_channel = value
            self._uart_midi.out_channel = value
        if self._usb_midi:
            self._usb_midi.in_channel = value
            self._usb_midi.out_channel = value
    def set_thru(self, value):
        self._thru = value

    def _process_message(self, msg):
        if not msg:
            return

        if isinstance(msg, NoteOn):
            if msg.velocity > 0.0:
                if self._note_on:
                    self._note_on(msg.note, msg.velocity / 127.0)
            elif self._note_off:
                self._note_off(msg.note)
        elif isinstance(msg, NoteOff):
            if self._note_off:
                self._note_off(msg.note)
        elif isinstance(msg, ControlChange):
            if self._control_change:
                self._control_change(msg.control, msg.value / 127.0)
        elif isinstance(msg, PitchBend):
            if self._pitch_bend:
                self._pitch_bend((msg.pitch_bend - 8192) / 8192)
        elif isinstance(msg, ProgramChange):
            if self._program_change:
                self._program_change(msg.patch)

        if self._thru:
            if self._uart_midi:
                self._uart_midi.send(msg)
            if self._usb_midi:
                self._usb_midi.send(msg)

        self._trigger_led()

    def _process_messages(self, midi, limit=32):
        while limit>0:
            msg = midi.receive()
            if not msg:
                break
            self._process_message(msg)
            limit = limit - 1

    def update(self):
        if self._uart_midi:
            self._process_messages(self._uart_midi)
        if self._usb_midi:
            self._process_messages(self._usb_midi)

        if self._led.value and time.monotonic() - self._led_last > self._led_duration:
            self._led.value = False

    def _trigger_led(self):
        self._led.value = True
        self._led_last = time.monotonic()

    def send_note_on(self, note, velocity):
        if self._uart_midi:
            self._uart_midi.send(NoteOn(note, velocity))
        if self._usb_midi:
            self._usb_midi.send(NoteOn(note, velocity))
        self._trigger_led()
    def send_note_off(self, note):
        if self._uart_midi:
            self._uart_midi.send(NoteOff(note))
        if self._usb_midi:
            self._usb_midi.send(NoteOff(note))
        self._trigger_led()
    def send_control_change(self, control, value):
        if self._uart_midi:
            self._uart_midi.send(ControlChange(control, value))
        if self._usb_midi:
            self._usb_midi.send(ControlChange(control, value))
        self._trigger_led()
