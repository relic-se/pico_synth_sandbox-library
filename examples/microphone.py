# pico_synth_sandbox - Microphone Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import time
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.microphone import Microphone
from pico_synth_sandbox.encoder import Encoder

display = Display()
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

microphone = Microphone()
max_level = 0.0

trigger_level = 25
trigger_level_step = 0.0001

def display_trigger():
    global max_level, trigger_level, trigger_level_step
    level_x = int(min(trigger_level*trigger_level_step/max_level, 1.0)*16) if max_level > 0.0 else 0
    display.write(" " * level_x + chr(0xff), (0,0))

def update_level():
    global max_level
    level = microphone.get_level()
    prev_max_level = max_level
    max_level = max(level, max_level)
    if max_level != prev_max_level:
        display_trigger()
    if max_level > 0.0:
        display.write_horizontal_graph(level, 0.0, max_level, (0,1), 16)
    else:
        display.write("", (0,1), 16)

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
encoder.set_long_press(start_record)

display.clear()
display_trigger()

while True:
    encoder.update()
    update_level()
