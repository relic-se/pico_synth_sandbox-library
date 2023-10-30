# pico_synth_sandbox - Filtered Synth Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

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

keyboard = TouchKeyboard()
arpeggiator = Arpeggiator()
arpeggiator.set_octaves(1)
arpeggiator.set_bpm(80)
arpeggiator.set_steps(Timer.STEP_EIGHTH)
arpeggiator.set_gate(0.5)
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity, keynum=None):
    if keynum is None:
        keynum = notenum - keyboard.root
    synth.press(keynum, notenum, velocity)
    display.write("*", (keynum % 12,1), 1)
keyboard.set_press(press)

def release(notenum, keynum=None):
    if keynum is None:
        keynum = notenum - keyboard.root
    synth.release(keynum)
    display.write("_", (keynum % 12,1), 1)
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

display.write("_"*12, (0,1))
while True:
    encoder.update()
    keyboard.update()
    synth.update()
