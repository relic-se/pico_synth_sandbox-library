# pico_synth_sandbox
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

from pico_synth_sandbox import *

# Wait for USB to stabilize
time.sleep(0.5)

gc.collect()

display = Display()
display.write("PicoSynthSandbox", (0,0))
display.write("Loading...", (0,1))

encoder = Encoder()

midi = Midi()

#audio = PWMAudio()

keyboard = TouchKeyboard()
arpeggiator = Arpeggiator()
keyboard.set_arpeggiator(arpeggiator)

def press(notenum, velocity):
    pass
    #voice.press(notenum, velocity)
keyboard.set_press(press)

def release(notenum):
    pass
    #voice.release()
keyboard.set_release(release)

def note_on(notenum, velocity):
    keyboard.append(notenum, velocity)
midi.set_note_on(note_on)

def note_off(notenum):
    keyboard.remove(notenum)
midi.set_note_off(note_off)

def control_change(control, value):
    if control == 64: # Sustain
        keyboard.set_sustain(value)
midi.set_control_change(control_change)

def pitch_bend(value):
    pass
    #voice.set_pitch_bend(value)
midi.set_pitch_bend(pitch_bend)

gc.collect()

display.write("Ready!", (0,1))

while True:
    encoder.update()
    keyboard.update()
    midi.update()
