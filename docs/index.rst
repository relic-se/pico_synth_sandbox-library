.. pico_synth_sandbox documentation master file, created by
   sphinx-quickstart on Wed Oct 11 14:19:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pico_synth_sandbox Documentation
================================

Raspberry Pi Pico digital synthesizer board with I2S or PWM audio, a PDM microphone, MIDI i/o, a capacitive keybed, 1602 display, a rotary encoder, and LiPo battery. Designed for use with CircuitPython and synthio.

Features
--------

* PCM5102 I2S DAC module compatibility or with populated components
* Optional PWM audio output
* LiPo Battery usb charging and power supply controlled by 3v3_enable
* MIDI input and output via MIDI TRS-A 3.5mm jack (compatible with most adapters)
* Dedicated volume pot with on-board speaker and line output
* 12 capacitive sense touch buttons serving as a single-octave keybed
* Software reset button
* 1602 display and rotary encoder with switch
* Optional PDM Microphone

RP2040 Pin Assignment
---------------------

Some pins require solder jumper configuration if you do not use the default pin assignment for MIDI & I2S.

Table of Contents
=================

.. toctree::
    :maxdepth: 3

    Home<self>
    examples
    api

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
