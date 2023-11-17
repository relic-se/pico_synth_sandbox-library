# pico_synth_sandbox - Microphone FFT Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import math
import ulab.numpy as numpy
from pico_synth_sandbox import fft
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.microphone import Microphone

display = Display()
display.enable_vertical_graph()

microphone = Microphone()

segments = 16
spectro_range = 0.33
min_val = None
max_val = None

while True:
    fft_data = fft(microphone.get_buffer(256), log=True, dtype=numpy.uint16)

    segment_len = int(math.floor(len(fft_data)*spectro_range/segments))
    segment_data = [0 for i in range(segments)]
    for i in range(segments):
        segment_data[i] = numpy.max(fft_data[i*segment_len:(i+1)*segment_len])

    if min_val is None:
        min_val = numpy.min(segment_data)
    else:
        min_val = min(numpy.min(segment_data), min_val)

    if max_val is None:
        max_val = numpy.max(segment_data)
    else:
        max_val = max(numpy.max(segment_data), max_val)

    for i in range(segments):
        display.write_vertical_graph(
            value = segment_data[i],
            minimum = min_val,
            maximum = max_val,
            position = (i,0),
            height = 2
        )
    display.update(reset_cursor=False)
