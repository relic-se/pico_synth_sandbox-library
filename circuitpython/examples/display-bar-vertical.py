# pico_synth_sandbox - Vertical Bar Graph Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

display = Display()
display.enable_vertical_graph()

value = 0
def update_value():
    global value
    display.write(value, (13,0), 3, True, False)
    display.write_vertical_graph(
        value=value,
        minimum=0,
        maximum=100,
        position=(0,0),
        height=2,
        reset_cursor=False
    )
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

while True:
    encoder.update()

