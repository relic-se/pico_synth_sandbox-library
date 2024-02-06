# pico_synth_sandbox - Drums Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import pico_synth_sandbox.tasks
from pico_synth_sandbox.board import get_board
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.drum import Kick, Snare, ClosedHat, OpenHat
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.arpeggiator import Arpeggiator

board = get_board()

display = Display(board)
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))
display.force_update()

audio = get_audio_driver(board)
synth = Synth(audio)
synth.add_voice(Kick())
synth.add_voice(Snare())
# Keep local variable for changing envelope
closed_hat = ClosedHat()
open_hat = OpenHat()
synth.add_voice(closed_hat)
synth.add_voice(open_hat)

keyboard = get_keyboard_driver(board, max_voices=1)
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def voice_press(voice, notenum, velocity, keynum=None):
    voice = (notenum - keyboard.root) % len(synth.voices) # Ignore voice allocation
    synth.press(voice, notenum, velocity)
    if voice == 2: # Closed Hat
        synth.release(open_hat, True) # Force release
keyboard.set_voice_press(voice_press)

def voice_release(voice, notenum, keynum=None):
    voice = (notenum - keyboard.root) % len(synth.voices) # Ignore voice allocation
    synth.release(voice)
keyboard.set_voice_release(voice_release)

def key_press(keynum, notenum, velocity):
    display.write("*", (keynum,1), 1)
keyboard.set_key_press(key_press)

def key_release(keynum, notenum):
    display.write("_", (keynum,1), 1)
keyboard.set_key_release(key_release)

mod_value = 64
encoder = Encoder(board)
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

display.write("_"*len(keyboard.keys), (0,1))

pico_synth_sandbox.tasks.run()
