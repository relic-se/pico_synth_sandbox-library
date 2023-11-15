# pico_synth_sandbox/midi.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import clamp
import board, os, time
from digitalio import DigitalInOut, Direction
from busio import UART
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.midi_message import MIDIUnknownEvent

class Midi:
    """Send and receive both hardware UART and USB MIDI messages using :class:`adafruit_midi.MIDI`. UART can be enabled with the `MIDI_UART` variable and USB can be enabled with the `MIDI_USB` variable in `settings.toml`. The midi channel is limited to a single value for both input and output and is determined by the `MIDI_CHANNEL` variable in `settings.toml` with a range of 0-15. However, the channel can be changed once a :class:`pico_synth_sandbox.midi.Midi` object is created by calling the `set_channel` function. By default, the onboard led will be used to indicate incoming midi messages. At the moment, this feature cannot be disabled.
    """

    def __init__(self):
        self._channel = None
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
                debug=False
            )
        else:
            self._uart_midi = None

        if os.getenv("MIDI_USB", 0) > 0:
            self._usb_midi = adafruit_midi.MIDI(
                midi_in=usb_midi.ports[0],
                midi_out=usb_midi.ports[1],
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
        """Set the callback method you would like to be called when a `adafruit_midi.note_on.NoteOn` message is received.

        :param callback: The callback method. Must have 2 parameters for note value and velocity (0.0-1.0). Ie: `def note_on(notenum, velocity):`.
        :type callback: function
        """
        self._note_on = callback
    def set_note_off(self, callback):
        """Set the callback method you would like to be called when a `adafruit_midi.note_off.NoteOff` message is received.

        :param callback: The callback method. Must have 1 parameter for the note value. Ie: `def note_off(notenum):`.
        :type callback: function
        """
        self._note_off = callback
    def set_control_change(self, callback):
        """Set the callback method you would like to be called when a `adafruit_midi.control_change.ControlChange` message is received.

        :param callback: The callback method. Must have 2 parameters for control number and control value (0.0-1.0). Ie: `def control_change(control, value):`.
        :type callback: function
        """
        self._control_change = callback
    def set_pitch_bend(self, callback):
        """Set the callback method you would like to be called when a `adafruit_midi.pitch_bend.PitchBend` message is received.

        :param callback: The callback method. Must have 1 parameter for the pitch bend value (-1.0-1.0). Ie: `def pitch_bend(value):`.
        :type callback: function
        """
        self._pitch_bend = callback
    def set_program_change(self, callback):
        """Set the callback method you would like to be called when a `adafruit_midi.program_change.ProgramChange` message is received.

        :param callback: The callback method. Must have 1 parameter for the patch number requested. Ie: `def program_change(patch):`.
        :type callback: function
        """
        self._program_change = callback

    def set_channel(self, value):
        """Set the midi channel for messages to be received and sent from.

        :param value: The desired channel from 0 to 16. 0 will accept all midi messages.
        :type value: int
        """
        if value == 0 or value is None:
            value = None
        else:
            value = clamp(value - 1, 0, 15)
        self._channel = value
    def get_channel(self):
        return 0 if self._channel is None else self._channel + 1
    
    def set_thru(self, value):
        """Set whether you would like to forward incoming midi messages through the enabled outputs automatically.

        :param value: Whether or not you would like to enable midi thru.
        :type value: bool
        """
        self._thru = value
    def get_thru(self):
        return self._thru

    def _process_message(self, msg):
        if not msg:
            return
        
        if self._channel is None or msg.channel == self._channel:
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

        if self._thru and not isinstance(msg, MIDIUnknownEvent):
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
        """Process any incoming midi messages from the enabled midi devices. Will trigger any pre-defined callbacks if the appropriate messages are received.
        """
        if self._uart_midi:
            self._process_messages(self._uart_midi)
        if self._usb_midi:
            self._process_messages(self._usb_midi)

        if self._led.value and time.monotonic() - self._led_last > self._led_duration:
            self._led.value = False

    def _trigger_led(self):
        self._led.value = True
        self._led_last = time.monotonic()

    def send_note_on(self, notenum, velocity=1.0):
        """Send an :class:`adafruit_midi.note_on.NoteOn` message through the enabled midi outputs.

        :param notenum: The value of the midi note to send.
        :type notenum: int
        :param velocity: The velocity of the note from 0.0 through 1.0.
        :type velocity: float
        """
        velocity = int(clamp(velocity) * 127.0)
        msg = NoteOn(notenum, velocity, channel=self._channel)
        if self._uart_midi:
            self._uart_midi.send(msg)
        if self._usb_midi:
            self._usb_midi.send(msg)
        self._trigger_led()
    def send_note_off(self, notenum):
        """Send an :class:`adafruit_midi.note_off.NoteOff` message through the enabled midi outputs.

        :param notenum: The value of the midi note to send.
        :type notenum: int
        """
        msg = NoteOff(notenum, channel=self._channel)
        if self._uart_midi:
            self._uart_midi.send(msg)
        if self._usb_midi:
            self._usb_midi.send(msg)
        self._trigger_led()
    def send_control_change(self, control, value):
        """Send an :class:`adafruit_midi.control_change.ControlChange` message through the enabled midi outputs.

        :param control: The number of the midi control to send.
        :type control: int
        :param value: The value to set of the desired control from 0.0 through 1.0.
        :type value: float
        """
        value = int(clamp(value) * 127.0)
        msg = ControlChange(control, value, channel=self._channel)
        if self._uart_midi:
            self._uart_midi.send(msg)
        if self._usb_midi:
            self._usb_midi.send(msg)
        self._trigger_led()
