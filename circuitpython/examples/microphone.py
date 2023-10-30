# pico_synth_sandbox - Microphone Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

display = Display()
display.enable_horizontal_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

microphone = Microphone()
max_level = 0.0
def update(level):
    global max_level
    max_level = max(level, max_level)
    display.write_horizontal_graph(level, 0.0, max_level, (0,1), 16)
microphone.set_update(update)
def trigger():
    display.write("Recording", (0,0), 13)
microphone.set_trigger(trigger)

trigger_level = 10
def update_trigger_level():
    global trigger_level
    microphone.set_trigger_level(trigger_level / 1000.0)
    display.write(trigger_level, (13,0), 3, True)
update_trigger_level()
encoder = Encoder()
def increment():
    global trigger_level
    if trigger_level < 100:
        trigger_level += 1
        update_trigger_level()
encoder.set_increment(increment)
def decrement():
    global trigger_level
    if trigger_level > 1:
        trigger_level -= 1
        update_trigger_level()
encoder.set_decrement(decrement)
def click():
    display.write("Waiting", (0,0), 13)
    microphone.record("test")
    display.write("Complete!")
    time.sleep(1)
    display.write("Press Button", (0,0), 13)
encoder.set_click(click)

display.write("Press Button", (0,0), 13)
while True:
    encoder.update()
    microphone.update()
