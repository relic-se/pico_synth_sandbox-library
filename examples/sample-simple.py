# pico_synth_sandbox - Simple Sample Playback Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import pico_synth_sandbox.tasks
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.arpeggiator import Arpeggiator
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

audio = get_audio_driver()
synth = Synth(audio)
synth.add_voice(Sample(loop=False, filepath="/samples/hey.wav"))

keyboard = get_keyboard_driver(root=60)
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity, keynum=None):
    if keynum is None:
        keynum = (notenum - keyboard.root) % len(keyboard.keys)
    synth.press(0, notenum, velocity)
    display.write("*", (keynum,1), 1)
keyboard.set_press(press)

def release(notenum, keynum=None):
    if keynum is None:
        keynum = (notenum - keyboard.root) % len(keyboard.keys)
    synth.release(0)
    display.write("_", (keynum,1), 1)
keyboard.set_release(release)

encoder = Encoder()
def click():
    arpeggiator.toggle()
encoder.set_click(click)
encoder.set_long_press(click)

display.write("_"*len(keyboard.keys), (0,1))

pico_synth_sandbox.tasks.run()
