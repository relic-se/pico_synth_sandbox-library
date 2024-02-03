# pico_synth_sandbox - Sample Browser Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import gc, os
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
synth = Synth(audio)
synth.add_voices(Sample(loop=False) for i in range(4))
for voice in synth.voices:
    voice.set_envelope(
        attack_time=0.05,
        decay_time=0.1,
        release_time=0.0,
        attack_level=0.5,
        sustain_level=0.5
    )

sample_data = None
sample_rate = audio.get_sample_rate()
sample_root = 440.0

sample_files = list(filter(lambda x: x[-4:] == ".wav", os.listdir("/samples")))
if not sample_files:
    print("No samples available. Try running \"make samples --always-make\" in the library root directory.")
    exit()

keyboard = get_keyboard_driver(board, root=60, max_voices=len(synth.voices))
def press(voice, notenum, velocity, keynum=None):
    synth.press(voice, notenum, velocity)
keyboard.set_voice_press(press)
def release(voice, notenum, keynum=None):
    synth.release(voice)
keyboard.set_voice_release(release)

type = 0
semitone = 0
sample_index = 0
sample_index_loaded = -1

def update_cursor():
    global type
    display.set_cursor_position(5 if type else 0, 0)

def update_tune(write=True):
    global semitone
    for voice in synth.voices:
        voice.set_coarse_tune(semitone / 12.0)
    if write:
        display.write_horizontal_graph(semitone, -24, 24, (0,1), 4)

def update_sample():
    global sample_index, sample_index_loaded
    display.write(sample_files[sample_index][:-4], (5,1))
    display.write("*" if sample_index == sample_index_loaded else " ", (15,0), 1)

def increment_tune():
    global type, semitone
    if type != 0:
        type = 0
        update_cursor()
    if semitone < 24:
        semitone += 1
        update_tune()
def decrement_tune():
    global type, semitone
    if type != 0:
        type = 0
        update_cursor()
    if semitone > -24:
        semitone -= 1
        update_tune()

def increment_sample():
    global type, sample_index, sample_files
    if type != 1:
        type = 1
        update_cursor()
    sample_index = (sample_index + 1) % len(sample_files)
    update_sample()
def decrement_sample():
    global type, sample_index, sample_files
    if type != 1:
        type = 1
        update_cursor()
    sample_index = (sample_index - 1) % len(sample_files)
    update_sample()

def load_sample(write=True):
    global semitone, sample_data, sample_rate, sample_root, sample_index, sample_index_loaded
    if sample_index == sample_index_loaded:
        return
    
    pico_synth_sandbox.tasks.pause()
    audio.mute()
    if write:
        display.write("Loading...", (5,1))
        display.update()

    for voice in synth.voices:
        voice.unload()
    del sample_data
    gc.collect()

    semitone = 0
    update_tune(write)

    sample_data, sample_rate = waveform.load_from_file("/samples/" + sample_files[sample_index], max_samples=8192)
    sample_root = fftfreq(
        data=sample_data,
        sample_rate=sample_rate
    )
    for voice in synth.voices:
        voice.load(sample_data, sample_rate, sample_root)

    sample_index_loaded = sample_index
    if write: update_sample()
    audio.unmute()
    pico_synth_sandbox.tasks.resume()

if board.num_encoders() == 1:

    encoder = Encoder(board)

    def next():
        global type
        if type == 0:
            increment_tune()
        else:
            increment_sample()
    encoder.set_increment(next)

    def previous():
        global type
        if type == 0:
            increment_tune()
        else:
            increment_sample()
    encoder.set_decrement(previous)

    def toggle():
        global type
        type = 0 if type else 1
        update_cursor()
    encoder.set_click(toggle)

    encoder.set_long_press(load_sample)

elif board.num_encoders() > 1:

    encoder1 = Encoder(board, 0)
    encoder1.set_increment(increment_tune)
    encoder1.set_decrement(decrement_tune)

    encoder2 = Encoder(board, 1)
    encoder2.set_increment(increment_sample)
    encoder2.set_decrement(decrement_sample)
    encoder2.set_click(load_sample)

display.clear()
display.write("Tune Sample", position=(0,0))
display.set_cursor_enabled(True)
display.set_cursor_blink(True)
update_tune()
update_sample()

pico_synth_sandbox.tasks.run()
