# pico_synth_sandbox - Microphone Sample Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import gc, time
import pico_synth_sandbox.tasks
from pico_synth_sandbox.tasks import Task
from pico_synth_sandbox import fftfreq, normalize
from pico_synth_sandbox.board import get_board
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.microphone import Microphone

board = get_board()

display = Display(board)
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))
display.update()

audio = get_audio_driver(board)
synth = Synth(audio)
voice = Sample(loop=False)
synth.add_voice(voice)
voice.set_envelope(
    attack_time=0.05,
    decay_time=0.1,
    release_time=0.0,
    attack_level=0.75,
    sustain_level=0.75
)
voice.set_filter(
    type=Synth.FILTER_LPF,
    frequency=1.0,
    resonance=0.5,
    synth=synth
)

keyboard = get_keyboard_driver(board, root=60)

def press(notenum, velocity, keynum=None):
    if keynum is None:
        keynum = (notenum - keyboard.root) % len(keyboard.keys)
    synth.press(0, notenum, velocity)
keyboard.set_press(press)

def release(notenum, keynum=None):
    if keynum is None:
        keynum = (notenum - keyboard.root) % len(keyboard.keys)
    synth.release(0)
keyboard.set_release(release)

microphone = Microphone(board)

class MicrophoneLevel(Task):
    def __init__(self, microphone, update=None):
        self._microphone = microphone
        self._max_level = 0.0
        self._update = update
        Task.__init__(self, update_frequency=5)
    async def update(self):
        self._level = self._microphone.get_level()
        self._max_level = max(self._level, self._max_level)
        if self._update:
            self._update(self._level, self._max_level)
def update_level(level, max_level):
    if max_level > 0.0:
        display.write_horizontal_graph(level, 0.0, max_level, (12,1), 4)
    else:
        display.write("", (12,1), 4)
mic_level = MicrophoneLevel(microphone, update_level)

def trigger():
    display.write("Recording")
    display.update()
microphone.set_trigger(trigger)

type = 0
semitone = 0
filter = 100

def update_tune(write=True):
    global semitone
    voice.set_coarse_tune(semitone / 12.0)
    if write:
        display.write_horizontal_graph(semitone, -24, 24, (0,1), 4)

def update_filter(write=True):
    global filter
    voice.set_filter_frequency(filter / 100.0, synth)
    if write:
        display.write_horizontal_graph(filter, 0, 100, (5,1), 6)

def update_cursor():
    global type
    display.set_cursor_position(5 if type else 0, 0)

def reset_display():
    display.clear()
    display.write("Tune Filter Mic", (0,0))
    update_tune()
    update_filter()
    update_cursor()
    display.set_cursor_enabled(True)
    display.set_cursor_blink(True)

def start_record():
    global semitone

    pico_synth_sandbox.tasks.pause()
    audio.mute()
    display.set_cursor_enabled(False)
    display.set_cursor_blink(False)
    display.clear()

    semitone = 0
    update_tune(False)

    voice.unload()
    gc.collect()

    display.write("Waiting")
    display.update()

    sample_data = microphone.read(
        samples=4096,
        trigger=0.01,
        clip=0.001
    )

    display.write("Processing")
    display.update()

    # Normalize Volume
    sample_data = normalize(sample_data)

    # Calculate root frequency
    sample_rate = Microphone.get_sample_rate()
    sample_root = fftfreq(
        data=sample_data,
        sample_rate=sample_rate
    )
    voice.load(sample_data, sample_rate, sample_root)

    display.clear()
    display.write("Complete!")
    display.update()
    time.sleep(0.5)

    reset_display()
    audio.unmute()
    pico_synth_sandbox.tasks.resume()

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
        update_cursor()
    encoder.set_click(toggle_encoder)

    encoder.set_long_press(start_record)

elif board.num_encoders() > 1:

    encoder1 = Encoder(board, 0)
    encoder1.set_increment(increment_semitone)
    encoder1.set_decrement(decrement_semitone)
    encoder1.set_long_press(start_record)

    encoder2 = Encoder(board, 1)
    encoder2.set_increment(increment_filter)
    encoder2.set_decrement(decrement_filter)
    encoder2.set_long_press(start_record)

# Wait for microphone to initialize
time.sleep(1)

reset_display()

pico_synth_sandbox.tasks.run()
