# pico_synth_sandbox - Filtered Sample Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import random
import pico_synth_sandbox.tasks
from pico_synth_sandbox import fftfreq
from pico_synth_sandbox.board import get_board
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample
import pico_synth_sandbox.waveform as waveform

board = get_board()

display = Display(board)
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))
display.update()

audio = get_audio_driver(board)
audio.mute()

sample_data, sample_rate = waveform.load_from_file("/samples/hey.wav")
root = fftfreq(
    data=sample_data,
    sample_rate=sample_rate
)

synth = Synth(audio)
synth.add_voices(Sample(loop=True) for i in range(4))
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

keyboard = get_keyboard_driver(board, max_voices=len(synth.voices))
def press(voice, notenum, velocity, keynum=None):
    synth.press(voice, notenum, velocity)
keyboard.set_voice_press(press)
def release(voice, notenum, keynum=None):
    synth.release(voice)
keyboard.set_voice_release(release)

type = 0
semitone = 0
filter = 100

def update_cursor():
    global type
    display.set_cursor_position(8 if type else 0, 0)
update_cursor()

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

def increment_semitone():
    global type, semitone
    if type != 0:
        type = 0
        update_cursor()
    if semitone < 24:
        semitone += 1
        update_tune()
def decrement_semitone():
    global type, semitone
    if type != 0:
        type = 0
        update_cursor()
    if semitone > -24:
        semitone -= 1
        update_tune()

def increment_filter():
    global type, filter
    if type != 1:
        type = 1
        update_cursor()
    if filter < 100:
        filter += 1
        update_filter()
def decrement_filter():
    global type, filter
    if type != 1:
        type = 1
        update_cursor()
    if filter > 0:
        filter -= 1
        update_filter()

if board.num_encoders() == 1:

    encoder = Encoder(board)

    def increment_encoder():
        global type
        if type == 0:
            increment_semitone()
        else:
            increment_filter()
    encoder.set_increment(increment_encoder)

    def decrement_encoder():
        global type
        if type == 0:
            increment_semitone()
        else:
            increment_filter()
    encoder.set_decrement(decrement_encoder)

    def toggle_encoder():
        global type
        type = 0 if type else 1
        display.set_cursor_position(5 if type else 0, 0)
    encoder.set_click(toggle_encoder)
    encoder.set_long_press(toggle_encoder)

elif board.num_encoders() > 1:

    encoder1 = Encoder(board, 0)
    encoder1.set_increment(increment_semitone)
    encoder1.set_decrement(decrement_semitone)

    encoder2 = Encoder(board, 1)
    encoder2.set_increment(increment_filter)
    encoder2.set_decrement(decrement_filter)


display.write("Tune    Filter  ", position=(0,0))
display.set_cursor_enabled(True)
display.set_cursor_blink(True)
display.update()

audio.unmute()

pico_synth_sandbox.tasks.run()
