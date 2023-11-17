# pico_synth_sandbox - Horizontal Bar Graph Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import pico_synth_sandbox.tasks
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder

display = Display()
display.enable_horizontal_graph()

value = 0
def update_value():
    global value
    display.write(value, (0,0), 3, False)
    display.write_horizontal_graph(
        value=value,
        minimum=0,
        maximum=100,
        position=(0,1),
        width=16
    )
    display.refresh(reset_cursor=False)
update_value()

encoder = Encoder()
def increment():
    global value
    if value < 100:
        value += 1
        update_value()
encoder.set_increment(increment)
def decrement():
    global value
    if value > 0:
        value -= 1
        update_value()
encoder.set_decrement(decrement)

pico_synth_sandbox.tasks.run()
