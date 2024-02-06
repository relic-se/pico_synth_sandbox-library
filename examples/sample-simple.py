# pico_synth_sandbox - Simple Sample Playback Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import pico_synth_sandbox.tasks
from pico_synth_sandbox.board import get_board
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.arpeggiator import Arpeggiator
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample

board = get_board()

display = Display(board)
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))
display.force_update()

audio = get_audio_driver(board)
audio.mute()
synth = Synth(audio)
synth.add_voice(Sample(loop=False, filepath="/samples/hey.wav"))

keyboard = get_keyboard_driver(board, root=60, max_voices=len(synth.voices))
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def voice_press(voice, notenum, velocity, keynum=None):
    synth.press(0, notenum, velocity)
keyboard.set_voice_press(voice_press)

def voice_release(voice, notenum, keynum=None):
    if not synth.has_notes():
        synth.release(0)
keyboard.set_voice_release(voice_release)

def key_press(keynum, notenum, velocity):
    display.write("*", (keynum,1), 1)
keyboard.set_key_press(key_press)

def key_release(keynum, notenum):
    display.write("_", (keynum,1), 1)
keyboard.set_key_release(key_release)

encoder = Encoder(board)
def click():
    arpeggiator.toggle()
encoder.set_click(click)
encoder.set_long_press(click)

display.write("_"*len(keyboard.keys), (0,1))

audio.unmute()

pico_synth_sandbox.tasks.run()
