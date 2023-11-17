# pico_synth_sandbox - Filtered Synth Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import pico_synth_sandbox.tasks
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.oscillator import Oscillator
from pico_synth_sandbox.waveform import Waveform
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.arpeggiator import Arpeggiator

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))
display.refresh()

audio = get_audio_driver()
synth = Synth(audio)
synth.add_voices(Oscillator() for i in range(12))
synth.set_waveform(Waveform.get_saw())
for voice in synth.voices:
    voice.set_envelope(
        attack_time=0.1,
        decay_time=0.2,
        release_time=1.0,
        attack_level=1.0,
        sustain_level=0.5
    )
    voice.set_filter(
        type=Synth.FILTER_LPF,
        frequency=1.0,
        resonance=0.5,
        envelope_attack_time=1.0,
        envelope_release_time=1.0,
        envelope_amount=0.05,
        lfo_rate=0.5,
        lfo_depth=0.05,
        synth=synth
    )

keyboard = get_keyboard_driver()
arpeggiator = Arpeggiator()
arpeggiator.set_octaves(1)
arpeggiator.set_bpm(80)
arpeggiator.set_steps(Arpeggiator.STEP_EIGHTH)
arpeggiator.set_gate(0.5)
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity, keynum=None):
    if keynum is None:
        keynum = (notenum - keyboard.root) % len(keyboard.keys)
    synth.press(keynum % 12, notenum, velocity)
    display.write("*", (keynum,1), 1)
    display.refresh()
keyboard.set_press(press)

def release(notenum, keynum=None):
    if keynum is None:
        keynum = (notenum - keyboard.root) % len(keyboard.keys)
    synth.release(keynum % 12)
    display.write("_", (keynum,1), 1)
    display.refresh()
keyboard.set_release(release)

mod_value = 127
encoder = Encoder()
def update_filter():
    synth.set_filter_frequency(float(mod_value) / 127.0)
def increment():
    global mod_value
    if mod_value < 127:
        mod_value += 1
        update_filter()
def decrement():
    global mod_value
    if mod_value > 0:
        mod_value -= 1
        update_filter()
def click():
    arpeggiator.toggle()
encoder.set_increment(increment)
encoder.set_decrement(decrement)
encoder.set_click(click)
encoder.set_long_press(click)

display.write("_"*len(keyboard.keys), (0,1))
display.refresh()

pico_synth_sandbox.tasks.run()
