# pico_synth_sandbox - Drums Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

audio = get_audio_driver()
synth = Synth(audio)
synth.add_voice(Kick())
synth.add_voice(Snare())
# Keep local variable for changing envelope
closed_hat = ClosedHat()
open_hat = OpenHat()
synth.add_voice(closed_hat)
synth.add_voice(open_hat)

keyboard = TouchKeyboard()
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity, keynum=None):
    if keynum is None:
        keynum = notenum - keyboard.root
    synth.press(keynum, notenum, velocity)
    if keynum % 12 == 2: # Closed Hat
        synth.release(open_hat, True) # Force release
    display.write("*", (keynum,1), 1)
keyboard.set_press(press)

def release(notenum, keynum=None):
    if keynum is None:
        keynum = notenum - keyboard.root
    synth.release(keynum)
    display.write("_", (keynum,1), 1)
keyboard.set_release(release)

mod_value = 64
encoder = Encoder()
def update_envelope():
    closed_hat.set_time(float(mod_value) / 127.0)
    open_hat.set_time(float(mod_value) / 127.0)
def increment():
    global mod_value
    if mod_value < 127:
        mod_value += 1
        update_envelope()
def decrement():
    global mod_value
    if mod_value > 0:
        mod_value -= 1
        update_envelope()
def click():
    arpeggiator.toggle()
encoder.set_increment(increment)
encoder.set_decrement(decrement)
encoder.set_click(click)
encoder.set_long_press(click)

display.write("_"*12, (0,1))
while True:
    encoder.update()
    keyboard.update()
    synth.update()
