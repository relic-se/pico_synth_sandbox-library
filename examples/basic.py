# pico_synth_sandbox - Basic Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import time
from pico_synth_sandbox.board import get_board
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.oscillator import Oscillator

board = get_board()
audio = get_audio_driver(board)
synth = Synth(audio)
synth.add_voice(Oscillator())

while True:
    synth.press(notenum=46)
    time.sleep(1)
    synth.release()
    time.sleep(1)
