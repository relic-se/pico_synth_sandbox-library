# pico_synth_sandbox - Basic Example
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

audio = get_audio_driver()
synth = Synth(audio)
synth.add_voice(Oscillator())

while True:
    synth.press(notenum=46)
    time.sleep(1)
    synth.release()
    time.sleep(1)
