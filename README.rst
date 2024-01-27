pico_synth_sandbox
==================

.. image:: https://readthedocs.org/projects/pico-synth-sandbox/badge/?version=latest
    :target: https://pico-synth-sandbox.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0
    :alt: GPL v3 License

A CircuitPython library designed for the `pico_synth_sandbox device <https://github.com/dcooperdalrymple/pico_synth_sandbox-hardware>`_ to provide hardware abstraction and a number of additional audio synthesis features.

Features
--------

* Device-level settings using ``settings.toml`` file to generate audio driver, display, MIDI, and other hardware objects
* Keyboard handling for key priority and voice allocation
* Arpeggiator and sequencer classes based on ``Timer`` class with support for bpm, step, and gate
* Waveform generator to quickly create numpy arrays
* Voice based structure to simplify note and parameter management among multiple ``synthio.Note`` instances
* Multiple voice types available:

  * Fully featured ``Oscillator`` with glide, pitch bend, frequency lfo (vibrato), amplitude envelope and lfo (tremolo), filter envelope and lfo, and panning lfo
  * Analog-based ``Drum`` voices: ``Kick``, ``Snare``, ``ClosedHat`` and ``OpenHat``
  * ``Sample`` voice with WAV audio file support, auto-tuning, and all aforemented ``Oscillator`` features

* Time-based synthio helpers for advanced block inputs (``LerpBlockInput`` and ``AREnvelope``)
* PDM Microphone level monitoring and trigger-based recording
* General audio helper functions such as FFT, resampling, and normalization

Examples
--------

A number of examples of available in the ``./examples`` folder which demonstrate the use and capabilities of this library. Further information about each example can be found within the `documentation <https://pico-synth-sandbox.readthedocs.io/en/latest/examples.html>`_.

Audio Samples
~~~~~~~~~~~~~

A few of the provided examples use pre-recorded audio samples for playback. These samples have been provided royalty-free within the ``./samples`` directory and can be automatically uploaded to your device using ``make samples`` in the root directory.

Installation
------------

1. Download and install CircuitPython bootloader: `instructions & UF2 file <https://circuitpython.org/board/raspberry_pi_pico/>`_. Requires version 9.0.0-alpha6 or greater.
2. Ensure that your device is connected and mounted as `CIRCUITPYTHON`.
3. Copy `requirements.txt` to the root folder of your device, make sure that the `circup` tool is installed in your environment with `pip3 install circup`, and run `circup update` to install all necessary libraries onto your device.
4. Copy the desired code example to the root folder of your device as `code.py` and perform a software reset to run the code.

.. note::
    Alternatively, you can run the included makefile with `make` to automatically install and update your CircuitPython device (CircuitPython must first be configured).

Dependencies
~~~~~~~~~~~~

* `asyncio <https://docs.circuitpython.org/projects/asyncio/>`_
* `adafruit_debouncer <https://docs.circuitpython.org/projects/debouncer/>`_
* `adafruit_midi <https://docs.circuitpython.org/projects/midi/>`_
* `adafruit_character_lcd <https://docs.circuitpython.org/projects/charlcd/>`_
* `adafruit_wave <https://docs.circuitpython.org/projects/wave/>`_

Documentation
-------------

Documentation for the included CircuitPython library can be found on `Read the Docs <https://pico-synth-sandbox.readthedocs.io/>`_.

Attribution
-----------

* Project inspired by `todbot/pico_test_synth <https://github.com/todbot/pico_test_synth>`_
