# pico_synth_sandbox - Microphone Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import time
import pico_synth_sandbox.tasks
from pico_synth_sandbox.tasks import Task
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.microphone import Microphone
from pico_synth_sandbox.encoder import Encoder

display = Display()
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

microphone = Microphone()

trigger_level = 25
trigger_level_step = 0.0001

class MicrophoneLevel(Task):
    def __init__(self, microphone, update=None):
        self._microphone = microphone
        self._max_level = 0.0
        self._prev_max_level = 0.0
        self._update = update
        Task.__init__(self, update_frequency=5)
    def set_update(self, callback):
        self._update = callback
    def update(self):
        self._level = self._microphone.get_level()
        self._prev_max_level = self._max_level
        self._max_level = max(self._level, self._max_level)
        if self._update:
            self._update(self._level, self._max_level, self._prev_max_level)
    def get_max_level(self):
        return self._max_level
mic_level = MicrophoneLevel(microphone)

def display_trigger():
    global trigger_level, trigger_level_step
    level_x = int(min(trigger_level*trigger_level_step/mic_level.get_max_level(), 1.0)*16) if mic_level.get_max_level() > 0.0 else 0
    display.write(" " * level_x + chr(0xff), (0,0))

def update_level(level, max_level, prev_max_level):
    if max_level != prev_max_level:
        display_trigger()
    if max_level > 0.0:
        display.write_horizontal_graph(level, 0.0, max_level, (0,1), 16)
    else:
        display.write("", (0,1), 16)
mic_level.set_update(update_level)

def record_trigger():
    display.write("Recording", (0,0), 13)
microphone.set_trigger(record_trigger)

encoder = Encoder()

def increment():
    global trigger_level
    if trigger_level < 100:
        trigger_level += 1
        display_trigger()
encoder.set_increment(increment)

def decrement():
    global trigger_level
    if trigger_level > 1:
        trigger_level -= 1
        display_trigger()
encoder.set_decrement(decrement)

def reset_max_level():
    global max_level
    max_level = 0.0
encoder.set_click(reset_max_level)

def start_record():
    pico_synth_sandbox.tasks.pause()
    display.clear()
    display.write("Waiting")
    microphone.record(
        name="test",
        samples=4096,
        trigger=trigger_level*trigger_level_step,
        clip=trigger_level*trigger_level_step
    )
    display.write("Complete!")
    time.sleep(1)
    display.clear()
    display_trigger()
    pico_synth_sandbox.tasks.resume()
encoder.set_long_press(start_record)

display.clear()
display_trigger()

pico_synth_sandbox.tasks.run()
