# pico_synth_sandbox - Midi Controller Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.midi import Midi
from pico_synth_sandbox.keyboard.touch import TouchKeyboard
from pico_synth_sandbox.arpeggiator import Arpeggiator

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

mod_value = 0

midi = Midi()
midi.set_thru(True)

keyboard = TouchKeyboard()
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity, keynum=None):
    midi.send_note_on(notenum, velocity)
    display.write("*", (keynum,1), 1)
keyboard.set_press(press)

def release(notenum, keynum=None):
    midi.send_note_off(notenum)
    display.write("_", (keynum,1), 1)
keyboard.set_release(release)

encoder = Encoder()
def increment():
    global mod_value
    if mod_value < 127:
        mod_value += 1
        midi.send_control_change(1, mod_value)
        display.write(str(mod_value), (13,1), 3, True)
def decrement():
    global mod_value
    if mod_value > 0:
        mod_value -= 1
        midi.send_control_change(1, mod_value)
        display.write(str(mod_value), (13,1), 3, True)
def click():
    arpeggiator.toggle()
encoder.set_increment(increment)
encoder.set_decrement(decrement)
encoder.set_click(click)

def control_change(control, value):
    if control == 64: # Sustain
        keyboard.set_sustain(value)
midi.set_control_change(control_change)

display.write("_"*12, (0,1))
display.write(str(mod_value), (13,1), 3, True)
while True:
    encoder.update()
    keyboard.update()
    midi.update()
