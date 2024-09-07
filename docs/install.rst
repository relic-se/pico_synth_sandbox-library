Firmware Installation
---------------------

1. Download and install CircuitPython bootloader: `instructions & UF2 file <https://circuitpython.org/board/raspberry_pi_pico/>`_. Requires version 9.0.0-alpha6 or greater.
2. Ensure that your device is connected and mounted as ``CIRCUITPYTHON``.
3. Copy ``requirements.txt`` to the root folder of your device, make sure that the ``circup`` tool is installed in your environment with ``pip3 install circup``, and run ``circup update`` to install all necessary libraries onto your device.
4. Download `pico_synth_sandbox.zip` from the `latest release on GitHub <https://github.com/dcooperdalrymple/pico_synth_sandbox/releases/latest/>`. Extract all files from this compressed archive and copy into the ``lib`` folder on your device.
5. Copy the desired code example to the root folder of your device as ``code.py`` and perform a software reset to run the code. If you would like instead, you can use mu or Thonny to write, transfer, and debug code files via the REPL terminal.

.. note::
    Alternatively, you can run the included makefile with ``make`` to automatically install and update your CircuitPython device (CircuitPython must first be configured).

Library Dependencies
--------------------

* `asyncio <https://docs.circuitpython.org/projects/asyncio/>`_
* `adafruit_debouncer <https://docs.circuitpython.org/projects/debouncer/>`_
* `adafruit_midi <https://docs.circuitpython.org/projects/midi/>`_
* `adafruit_character_lcd <https://docs.circuitpython.org/projects/charlcd/>`_
* `adafruit_wave <https://docs.circuitpython.org/projects/wave/>`_
