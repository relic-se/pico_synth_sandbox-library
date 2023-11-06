# pico_synth_sandbox - Filtered Sample Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import random
from pico_synth_sandbox import fftfreq
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.keyboard.touch import TouchKeyboard
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample
from pico_synth_sandbox.waveform import Waveform

display = Display()
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

audio = get_audio_driver()

sample_data, sample_rate = Waveform.load_from_file("/samples/hey.wav")
root = fftfreq(
    data=sample_data,
    sample_rate=sample_rate
)

synth = Synth(audio)
synth.add_voices(Sample(loop=True) for i in range(12))
for voice in synth.voices:
    voice.load(sample_data, sample_rate, root)
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
    voice.set_vibrato_depth(0.1)
    voice.set_vibrato_rate(8.0)
    voice.set_pan_rate(random.randint(0,80)/100.0+0.1)
    voice.set_pan_depth(0.8)

keyboard = TouchKeyboard()
def press(notenum, velocity, keynum=None):
    synth.press(keynum, notenum=notenum)
keyboard.set_press(press)
def release(notenum, keynum=None):
    synth.release(keynum)
keyboard.set_release(release)

encoder = Encoder()
type = 0
semitone = 0
filter = 100

display.write("Tune    Filter  ", position=(0,0))
display.set_cursor_enabled(True)
display.set_cursor_blink(True)

def update_tune():
    global semitone
    for voice in synth.voices:
        voice.set_coarse_tune(semitone / 12.0)
    display.write_horizontal_graph(semitone, -48, 48, (0,1), 8)
update_tune()

def update_filter():
    global filter
    synth.set_filter_frequency(filter / 100.0)
    display.write_horizontal_graph(filter, 0, 100, (8,1), 8)
update_filter()

def increment():
    global type, semitone, filter
    if type == 0:
        if semitone < 48:
            semitone += 1
            update_tune()
    elif filter < 100:
        filter += 1
        update_filter()
encoder.set_increment(increment)

def decrement():
    global type, semitone, filter
    if type == 0:
        if semitone > -48:
            semitone -= 1
            update_tune()
    elif filter > 0:
        filter -= 1
        update_filter()
encoder.set_decrement(decrement)

def toggle():
    global type
    type = 0 if type else 1
    display.set_cursor_position(8 if type else 0, 0)
encoder.set_click(toggle)
encoder.set_long_press(toggle)

while True:
    keyboard.update()
    encoder.update()
    synth.update()
