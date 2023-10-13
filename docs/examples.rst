Examples
========

Basic
-----

The most basic example of initiating an audio output and synth object.

.. literalinclude:: ../circuitpython/examples/basic.py
    :caption: circuitpython/examples/basic.py
    :linenos:

Simple Synth
------------

Use the display, touch keyboard, and encoder to control a basic synth object.

.. literalinclude:: ../circuitpython/examples/simple.py
    :caption: circuitpython/examples/simple.py
    :linenos:

Filtered Synth
--------------

Use the display, touch keyboard, and encoder to control a more advanced synth object with amplitude envelope and filter settings. Filter uses both an envelope and low-frequency oscillator ("lfo"). Synth object must call update function in program loop for envelope and lfo to operate.

.. literalinclude:: ../circuitpython/examples/filter.py
    :caption: circuitpython/examples/filter.py
    :linenos:

Midi Controller
---------------

Use the touch keyboard and encoder to output midi note and control messages through the UART midi interface.

.. literalinclude:: ../circuitpython/examples/midi.py
    :caption: circuitpython/examples/midi.py
    :linenos:

Drums
-----

Use the display, touch keyboard, and encoder to play synthesized drum samples using the provided Drum classes. Encoder controls decay time of closed and open hi hat.

.. literalinclude:: ../circuitpython/examples/drums.py
    :caption: circuitpython/examples/drums.py
    :linenos:
