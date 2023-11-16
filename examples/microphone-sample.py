# pico_synth_sandbox - Microphone Sample Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import gc, time
import pico_synth_sandbox.tasks
from pico_synth_sandbox.tasks import Task
from pico_synth_sandbox import fftfreq, normalize
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.microphone import Microphone

display = Display()
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

audio = get_audio_driver()
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

keyboard = get_keyboard_driver(root=60)

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

microphone = Microphone()

class MicrophoneLevel(Task):
    def __init__(self, microphone, update=None):
        self._microphone = microphone
        self._max_level = 0.0
        self._update = update
        Task.__init__(self, update_frequency=5)
    def update(self):
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
microphone.set_trigger(trigger)

encoder = Encoder()
type = 0
semitone = 0
filter = 100

def update_tune(write=True):
    global semitone
    voice.set_coarse_tune(semitone / 12.0)
    if write: display.write_horizontal_graph(semitone, -24, 24, (0,1), 4)

def update_filter(write=True):
    global filter
    voice.set_filter_frequency(filter / 100.0, synth)
    if write: display.write_horizontal_graph(filter, 0, 100, (5,1), 6)

def increment():
    global type, semitone, filter
    if type == 0:
        if semitone < 24:
            semitone += 1
            update_tune()
    elif filter < 100:
        filter += 1
        update_filter()
encoder.set_increment(increment)

def decrement():
    global type, semitone, filter
    if type == 0:
        if semitone > -24:
            semitone -= 1
            update_tune()
    elif filter > 0:
        filter -= 1
        update_filter()
encoder.set_decrement(decrement)

def toggle():
    global type
    type = 0 if type else 1
    display.set_cursor_position(5 if type else 0, 0)
encoder.set_click(toggle)

def reset_display():
    global type
    display.clear()
    display.write("Tune Filter Mic", (0,0))
    update_tune()
    update_filter()
    display.set_cursor_position(5 if type else 0, 0)
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

    sample_data = microphone.read(
        samples=4096,
        trigger=0.01,
        clip=0.001
    )

    display.write("Processing")

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
    time.sleep(0.5)

    reset_display()
    audio.unmute()
    pico_synth_sandbox.tasks.resume()
encoder.set_long_press(start_record)

# Wait for microphone to initialize
time.sleep(1)

reset_display()

pico_synth_sandbox.tasks.run()
