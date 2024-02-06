# pico_synth_sandbox - Sample Loop Points Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import pico_synth_sandbox.tasks
from pico_synth_sandbox.board import get_board
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.encoder import Encoder
from pico_synth_sandbox.keyboard import get_keyboard_driver
from pico_synth_sandbox.arpeggiator import Arpeggiator
from pico_synth_sandbox.audio import get_audio_driver
from pico_synth_sandbox.synth import Synth
from pico_synth_sandbox.voice.sample import Sample
import ulab.numpy as numpy

board = get_board()

display = Display(board)
display.enable_vertical_graph()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))
display.force_update()

audio = get_audio_driver(board)
audio.mute()
synth = Synth(audio)
voice = Sample(loop=True, filepath="/samples/acoustic-guitar.wav")
voice.set_glide(0.0)
voice.set_envelope(
    attack_time = 0.0,
    decay_time = 0.0,
    sustain_level = 1.0,
    release_time = 0.25
)
voice.set_coarse_tune(-2.0)
synth.add_voice(voice)

keyboard = get_keyboard_driver(board, root=60, max_voices=len(synth.voices))
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(index, notenum, velocity, keynum=None):
    synth.press(0, notenum, velocity)
keyboard.set_voice_press(press)

def release(index, notenum, keynum=None):
    if not synth.has_notes():
        synth.release(0)
keyboard.set_voice_release(release)

index = 0
loop = [0.0, 1.0]

def update_loop():
    global index, loop
    voice.set_loop(loop[0], loop[1])
    display.write("", (0,0), 16)
    display.write("}", (round(loop[1]*15),0), 1)
    display.write("{", (round(loop[0]*15),0), 1)
    display.set_cursor_position(round(loop[index]*15), 0)
def increment(i = None):
    global index, loop
    if not i is None: index = i
    loop[index] = min(loop[index] + 0.01, 1.0)
    update_loop()
def decrement(i = None):
    global index, loop
    if not i is None: index = i
    loop[index] = max(loop[index] - 0.01, 0.0)
    update_loop()

if board.num_encoders() == 1:

    encoder = Encoder(board)
    encoder.set_increment(increment)
    encoder.set_decrement(decrement)
    def toggle():
        global index
        index = 0 if index else 1
    encoder.set_click(toggle)
    encoder.set_long_press(toggle)

elif board.num_encoders() > 1:

    encoder1 = Encoder(board, 0)
    encoder1.set_increment(lambda : increment(0))
    encoder1.set_decrement(lambda : decrement(0))
    
    encoder2 = Encoder(board, 1)
    encoder2.set_increment(lambda : increment(1))
    encoder2.set_decrement(lambda : decrement(1))

display.clear()
segment_length = len(voice._note.waveform)//16
level = []
for i in range(16):
    segment = voice._note.waveform[i*segment_length:(i+1)*segment_length]
    level.append(numpy.sum(abs(segment)) / len(segment) / 32768.0)
max_level = max(level)
for i in range(16):
    display.write_vertical_graph(level[i], 0.0, max_level, position=(i,1), height=1)
update_loop()
display.set_cursor_enabled(True)
display.set_cursor_blink(True)

audio.unmute()

pico_synth_sandbox.tasks.run()
