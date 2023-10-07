# pico_synth_sandbox - Midi Controller Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

gc.collect()

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

mod_value = 0
keyboard_str = list("_" * 12)
def update_display():
    display.write("".join(keyboard_str), (0,1), 12)
    display.write(str(mod_value), (13,1), 3, True)

encoder = Encoder()

def increment():
    global mod_value
    if mod_value < 127:
        mod_value += 1
        midi.send_control_change(1, mod_value)
        update_display()
encoder.set_increment(increment)

def decrement():
    global mod_value
    if mod_value > 0:
        mod_value -= 1
        midi.send_control_change(1, mod_value)
        update_display()
encoder.set_decrement(decrement)

midi = Midi()
midi.set_thru(True)

keyboard = TouchKeyboard()
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity):
    midi.send_note_on(notenum, velocity)
    keyboard_str[(notenum - keyboard.root) % len(keyboard_str)] = "*"
    update_display()
keyboard.set_press(press)

def release(notenum):
    midi.send_note_off(notenum)
    keyboard_str[(notenum - keyboard.root) % len(keyboard_str)] = "_"
    update_display()
keyboard.set_release(release)

def control_change(control, value):
    if control == 64: # Sustain
        keyboard.set_sustain(value)
midi.set_control_change(control_change)

gc.collect()

update_display()

while True:
    encoder.update()
    keyboard.update()
    midi.update()
