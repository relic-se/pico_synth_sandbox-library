.. pico_synth_sandbox documentation master file, created by
   sphinx-quickstart on Wed Oct 11 14:19:48 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pico_synth_sandbox
==================

.. image:: https://readthedocs.org/projects/pico-synth-sandbox/badge/?version=latest
    :target: https://pico-synth-sandbox.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0
    :alt: GPL v3 License

A CircuitPython library designed for the `pico_synth_sandbox device <https://github.com/dcooperdalrymple/pico_synth_sandbox-hardware>`_ to provide hardware abstraction and a number of additional audio synthesis features.

.. list-table::

    * - .. image:: ../_static/front-side.jpg
            :alt: Front view of 3d rendered board
      - .. image:: ../_static/back-side.jpg
            :alt: Back view of 3d rendered board
      - .. image:: ../_static/bottom.jpg
            :alt: Bottom view of 3d rendered board

Features
--------

* Device-level settings using ``settings.toml`` file to generate audio driver, display, MIDI, and other hardware objects
* Keyboard handling for key priority and voice allocation
* :class:`pico_synth_sandbox.arpeggiator.Arpeggiator` and :class:`pico_synth_sandbox.sequencer.Sequencer` classes based on :class:`pico_synth_sandbox.timer.Timer` class with support for bpm, step, and gate
* :class:`pico_synth_sandbox.waveform.Waveform` generator to quickly create numpy arrays
* Voice based structure to simplify note and parameter management among multiple :class:`synthio.Note` instances
* Multiple :class:`pico_synth_sandbox.voice.Voice` types available:

  * Fully featured oscillator (:class:`pico_synth_sandbox.voice.oscillator.Oscillator`) with glide, pitch bend, frequency lfo (vibrato), amplitude envelope and lfo (tremolo), filter envelope and lfo, and panning lfo
  * Analog-based :class:`pico_synth_sandbox.voice.drum.Drum` voices: :class:`pico_synth_sandbox.voice.drum.Kick`, :class:`pico_synth_sandbox.voice.drum.Snare`, :class:`pico_synth_sandbox.voice.drum.ClosedHat` and :class:`pico_synth_sandbox.voice.drum.OpenHat`
  * :class:`pico_synth_sandbox.voice.sample.Sample` voice with WAV audio file support, auto-tuning, and all aforemented :class:`pico_synth_sandbox.voice.oscillator.Oscillator` features

* Time-based synthio helpers for advanced block inputs (:class:`pico_synth_sandbox.synth.LerpBlockInput` and :class:`pico_synth_sandbox.synth.AREnvelope`)
* :class:`pico_synth_sandbox.microphone.Microphone` level monitoring and trigger-based recording
* General audio helper functions such as FFT, resampling, and normalization

Table of Contents
=================

.. toctree::
    :maxdepth: 2

    Home<self>
    software
    examples
    library
    build

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
