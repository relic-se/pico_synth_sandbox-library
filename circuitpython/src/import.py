# pico_synth_sandbox
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import gc, os, sys, time, math, random, board
import ulab.numpy as numpy
import synthio
from audiomixer import Mixer

from digitalio import DigitalInOut, Direction, Pull
from busio import UART
from rotaryio import IncrementalEncoder
from touchio import TouchIn
from adafruit_debouncer import Debouncer, Button

import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.program_change import ProgramChange
from adafruit_midi.pitch_bend import PitchBend

from adafruit_character_lcd.character_lcd import Character_LCD_Mono

from pwmio import PWMOut
from audiopwmio import PWMAudioOut
from audiobusio import I2SOut
