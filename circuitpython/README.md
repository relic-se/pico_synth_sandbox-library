# CircuitPython Examples

## Installation

1. Download and install CircuitPython bootloader: [instructions & UF2 file](https://circuitpython.org/board/raspberry_pi_pico/).
2. Ensure that your device is connected and mounted as `CIRCUITPYTHON`.
3. Copy `requirements.txt` to the root folder of your device, make sure that the `circup` tool is installed in your environment with `pip3 install circup`, and run `circup update` to install all necessary libraries onto your device.
4. Copy the desired code example to the root folder of your device as `code.py` and perform a software reset to run the code.

_Alternatively, you can run the included makefile to automatically install and update your CircuitPython device (CircuitPython must first be configured)._

## Library Dependencies

* [asyncio](https://docs.circuitpython.org/projects/asyncio/)
* [adafruit_debouncer](https://docs.circuitpython.org/projects/debouncer/)
* [adafruit_midi](https://docs.circuitpython.org/projects/midi/)
* [adafruit_character_lcd](https://docs.circuitpython.org/projects/charlcd/)
* [adafruit_wave](https://docs.circuitpython.org/projects/wave/)
