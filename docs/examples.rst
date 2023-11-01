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

Monophonic Synth
----------------

Control two different oscillators in sync with a single note from the touch keyboard. The encoder is used to increase or decrease the pitch of both oscillators by semitones.

.. literalinclude:: ../circuitpython/examples/monophonic.py
    :caption: circuitpython/examples/monophonic.py
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

Drum Sequencer
--------------

Utilizes the Sequencer class to create a simple drum sequencer using the display, touch keyboard, encoder, and synthesized drum samples (similar to the "Drums" example). Encoder controls either the selected voice or beats per minute (aka "bpm") and is switched by clicking the encoder. There is a total of 16 steps used by the sequencer, and the first 8 keys can be used to toggle whether a note is played on that particular step for the selected voice. The 12th key is used to switch between the lower and upper 8 steps. The 9th through 11th keys are not used in this example.

.. literalinclude:: ../circuitpython/examples/sequencer.py
    :caption: circuitpython/examples/sequencer.py
    :linenos:

Microphone Example
------------------

Display the current microphone level as a horizontal bar graph. Set the record trigger and clip level using the encoder dial. Begin the record process by long pressing the encoder. The microphone will start recording when the input level is detected above the trigger level and will continue recording until the input level is detected below the clip level. The generated wave file will be saved to `/samples/test.wav`. Short click the encoder to reset the max level of the volume meter.

.. literalinclude:: ../circuitpython/examples/microphone.py
    :caption: circuitpython/examples/microphone.py
    :linenos:

Microphone FFT Example
----------------------

Use the included Fast Fourier Transform utility to calculate and display the range of frequencies from the microphone input as a row of vertical bar graphs.

.. literalinclude:: ../circuitpython/examples/microphone-fft.py
    :caption: circuitpython/examples/microphone-fft.py
    :linenos:

Simple Sample Playback Example
------------------------------

Create a `Sample` voice and load the included `/samples/hey.wav` file. File is loaded during voice initialization and only one monophonic voice is available. The sample voice is set to not loop playback. Use the encoder click to toggle the arpeggiator.

.. literalinclude:: ../circuitpython/examples/sample-simple.py
    :caption: circuitpython/examples/sample-simple.py
    :linenos:

Filtered Sample Example
-----------------------

Create 12 `Sample` voices using a single looping sample, the included `/samples/hey.wav` file. All of the available `Oscillator` parameters are defined to create a unique sound. Press the encoder to toggle between controlling the tune and filter frequency of the synthesizer.

.. literalinclude:: ../circuitpython/examples/sample-filter.py
    :caption: circuitpython/examples/sample-filter.py
    :linenos:

Sample Browser Example
----------------------

Browse through every wav sample available in the `/samples` directory. 12 `Sample` voices are created to play through selected sample using touch keyboard. Press the encoder to toggle between controlling the tune and scrolling through the samples. Perform a long press of the encoder to load the selected sample. An `*` indicator in the upper right corner of the screen will indicate if the currently selected sample is loaded.

.. literalinclude:: ../circuitpython/examples/sample-browser.py
    :caption: circuitpython/examples/sample-browser.py
    :linenos:

Microphone Sample Example
-------------------------

Use the microphone to record a sample into memory when the encoder is long pressed. The sample is then loaded into a simple `Sample` voice to play it back with the touch keyboard. You can control the pitch and filter of the voice using the encoder. Use a short click of the encoder to switch between the two options.

.. literalinclude:: ../circuitpython/examples/microphone-sample.py
    :caption: circuitpython/examples/microphone-sample.py
    :linenos:

Horizontal Bar Graph
--------------------

Use custom characters to draw a horizontal bar on the lcd display. Useful for demonstrating parameter values. **NOTE:** vertical and horizontal bars cannot be displayed simultaneously, and `display.enable_horizontal_graph` must be called prior to `display.write_horizontal_graph`.

.. literalinclude:: ../circuitpython/examples/display-bar-horizontal.py
    :caption: circuitpython/examples/display-bar-horizontal.py
    :linenos:

Vertical Bar Graph
--------------------

Use custom characters to draw a vertical bar on the lcd display. Useful for demonstrating levels. **NOTE:** vertical and horizontal bars cannot be displayed simultaneously, and `display.enable_vertical_graph` must be called prior to `display.write_vertical_graph`.

.. literalinclude:: ../circuitpython/examples/display-bar-vertical.py
    :caption: circuitpython/examples/display-bar-vertical.py
    :linenos:
