# pico_synth_sandbox - Simple Sample Playback Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

audio = get_audio_driver()
synth = Synth(audio)
synth.add_voice(Sample(loop=False, filepath="/samples/hey.wav"))

keyboard = TouchKeyboard(root=60)
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity, keynum=None):
    if keynum is None:
        keynum = notenum - keyboard.root
    synth.press(0, notenum, velocity)
    display.write("*", (keynum,1), 1)
keyboard.set_press(press)

def release(notenum, keynum=None):
    if keynum is None:
        keynum = notenum - keyboard.root
    synth.release(0)
    display.write("_", (keynum,1), 1)
keyboard.set_release(release)

encoder = Encoder()
def click():
    arpeggiator.toggle()
encoder.set_click(click)
encoder.set_long_press(click)

display.write("_"*12, (0,1))
while True:
    encoder.update()
    keyboard.update()
    synth.update()
