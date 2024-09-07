# pico_synth_sandbox/board.py
# 2024 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import board, os, microcontroller
from digitalio import DigitalInOut, Direction, Pull

class Board:
    """A hardware abstraction configuration utility to quickly designate between the capabilities and GPIO assignments of different board types. Official board revisions are provided, but custom board implementations can be defined by inheriting this class and defining public attributes.

    :param overclock: Whether or not to perform CPU overclocking if available within the class configuration.
    :type overclock: bool
    """

    def __init__(self, overclock:bool=True):
        """Constructor method
        """
        if overclock:
            self.overclock()

    led:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: The status LED. Typically designated to the built-in LED of the microcontroller.
    """
    def has_led(self) -> bool:
        """Check whether or not this board object has a status LED.
        
        :return: has led
        :rtype: bool
        """
        return not self.led is None
    def get_led(self) -> microcontroller.Pin:
        """Returns the assigned pin for the status LED if the board has one designated.
        
        :return: LED pin
        :rtype: :class:`microcontroller.Pin`
        """
        if not self.has_led(): return None
        pin = DigitalInOut(self.led)
        pin.direction = Direction.OUTPUT
        return pin
    
    encoders:list[tuple[microcontroller.Pin]] = []
    """list[tuple[:class:`microcontroller.Pin`]]: All of the available encoders in a list of Pin tuples. Ie: (pin_a, pin_b, pin_sw). If tuple is only 2 elements, switch will be excluded.
    """
    def has_encoders(self) -> bool:
        """Check whether or not the board has any encoders available.

        :return: has encoders
        :rtype: bool
        """
        return not self.encoders is None and len(self.encoders) > 0
    def get_encoder(self, index=0) -> tuple[IncrementalEncoder, DigitalInOut]:
        """Get the encoder at the designated index if valid. Returns both the :class:`rotaryio.IncrementalEncoder` and :class:`digitalio.DigitalInOut` objects in a tuple. If the encoder does not have a switch, it will be left as `None`. Only call this method once per encoder because it may otherwise throw GPIO conflict errors.

        :return: encoder and switch
        :rtype: tuple[:class:`rotaryio.IncrementalEncoder`, :class:`digitalio.DigitalInOut`]
        """
        if not self.has_encoders() or len(self.encoders) <= index or not len(self.encoders[index]) in [2,3]:
            return None
        from rotaryio import IncrementalEncoder
        encoder = IncrementalEncoder(self.encoders[index][0], self.encoders[index][1])
        button = None
        if len(self.encoders[index]) == 3:
            button = DigitalInOut(self.encoders[index][2])
            button.direction = Direction.INPUT
            button.pull = Pull.UP
        return (encoder, button)
    def get_encoders(self):
        """Get all encoder objects available on the board. Only call this method once because it may otherwise throw GPIO conflict errors. See :func:`~pico_synth_sandbox.board.Board.get_encoder` for full details of each list item.

        :return: all encoder and switch objects
        :rtype: list[tuple[:class:`rotaryio.IncrementalEncoder`, :class:`digitalio.DigitalInOut`]]
        """
        if not self.has_encoders():
            return None
        encoders = []
        for i in range(len(self.encoders)):
            encoders.append(self.get_encoder(i))
        return encoders
    def num_encoders(self) -> int:
        """Get the number of encoders available on the board.

        :return: count of encoders
        :rtype: int
        """
        if not self.has_encoders():
            return 0
        return len(self.encoders)

    uart_tx:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: MIDI UART TX.
    """
    uart_rx:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: MIDI UART RX.
    """
    def has_uart(self) -> bool:
        """Determine whether or not the board has hardware MIDI UART capabilities.

        :return: has midi uart
        :rtype: bool
        """
        return not self.uart_tx is None and not self.uart_rx is None
    def get_uart(self, baudrate=31250) -> UART:
        if not self.has_uart(): return None
        from busio import UART
        return UART(
            tx=self.uart_tx,
            rx=self.uart_rx,
            baudrate=baudrate,
            timeout=0.001
        )

    lcd_rs:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: Character LCD reset pin.
    """
    lcd_en:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: Character LCD enable pin.
    """
    lcd_d4:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: Character LCD D4 pin.
    """
    lcd_d5:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: Character LCD D5 pin.
    """
    lcd_d6:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: Character LCD D6 pin.
    """
    lcd_d7:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: Character LCD D7 pin.
    """
    def has_lcd(self) -> bool:
        """Determine whether or not the board has a character lcd display.

        :return: has midi uart
        :rtype: bool
        """
        return not self.lcd_rs is None and not self.lcd_en is None and not self.lcd_d4 is None and not self.lcd_d5 is None and not self.lcd_d6 is None and not self.lcd_d7 is None
    def get_lcd(self, columns:int=16, rows:int=2) -> Character_LCD_Mono:
        """Get the character lcd display object if available on the board.

        :param columns: The number of columns on the display. Defaults to 16.
        :type columns: int
        :param rows: The number of rows on the display. Defaults to 2.
        :return: lcd object
        :rtype: :class:`adafruit_character_lcd.character_lcd.Character_LCD_Mono`
        """
        if not self.has_lcd(): return None
        from adafruit_character_lcd.character_lcd import Character_LCD_Mono
        return Character_LCD_Mono(
            DigitalInOut(self.lcd_rs),
            DigitalInOut(self.lcd_en),
            DigitalInOut(self.lcd_d4),
            DigitalInOut(self.lcd_d5),
            DigitalInOut(self.lcd_d6),
            DigitalInOut(self.lcd_d7),
            columns,
            rows
        )
    
    pwm_out_left:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: The left PWM audio output pin.
    """
    pwm_out_right:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: The right PWM audio output pin.
    """
    def has_pwm_out(self) -> bool:
        """Whether or not the board supports PWM audio output.

        :return: has pwm audio output
        :rtype: bool
        """
        return not self.pwm_out_left is None and not self.pwm_out_right is None
    def get_pwm_out(self) -> PWMAudioOut:
        """Returns the :class:`audiopwmio.PWMAudioOut` object if the board supports PWM audio output.

        :return: audio output object
        :rtype: :class:`audiopwmio.PWMAudioOut`
        """
        if not self.has_pwm_out(): return None
        from audiopwmio import PWMAudioOut
        return PWMAudioOut(
            left_channel=self.pwm_out_left,
            right_channel=self.pwm_out_right
        )
    
    i2s_out_bit_clock:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: I2S audio output bit clock pin.
    """
    i2s_out_word_select:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: I2S audio output word select pin.
    """
    i2s_out_data:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: I2S audio output data pin.
    """
    def has_i2s_out(self) -> bool:
        """Whether or not the board supports I2S audio output.

        :return: i2s audio output support
        :rtype: bool
        """
        return not self.i2s_out_bit_clock is None and not self.i2s_out_word_select is None and not self.i2s_out_data is None
    def get_i2s_out(self) -> I2SOut:
        """Get the :class:`audiobusio.I2SOut` object if the board supports I2S audio output.

        :return: i2s audio output object
        :rtype: :class:`audiobusio.I2SOut`
        """
        if not self.has_i2s_out(): return None
        from audiobusio import I2SOut
        return I2SOut(
            bit_clock=self.i2s_out_bit_clock,
            word_select=self.i2s_out_word_select,
            data=self.i2s_out_data
        )
    
    def get_audio_out(self):
        """Get the primary audio output object depending on what hardware the board supports. If no audio output is supported, `None` will be returned.

        :return: audio output object
        :rtype: :class:`audiobusio.I2SOut` | :class:`audiopwmio.PWMAudioOut`
        """
        if self.has_i2s_out(): return self.get_i2s_out()
        if self.has_pwm_out(): return self.get_pwm_out()
        return None

    i2s_in_bit_clock:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: I2S audio input bit clock pin.
    """
    i2s_in_word_select:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: I2S audio input word select pin.
    """
    i2s_in_data:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: I2S audio input data pin.
    """
    def has_i2s_in(self) -> bool:
        """Whether or not the board supports I2S audio input.

        :return: i2s audio input support
        :rtype: bool
        """
        return not self.i2s_in_bit_clock is None and not self.i2s_in_word_select is None and not self.i2s_in_data is None
    def get_i2s_in(self):
        """Returns the I2S audio input object. Currently, I2S input is not supported by CircuitPython as of version 9.0.0. This method will be updated once support is available. Otherwise, it will always return `None`.
        """
        if not self.has_i2s_in(): return None
        # TODO
        return None
    
    pdm_clock:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: PDM audio input clock pin.
    """
    pdm_data:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: PDM audio input data pin.
    """
    def has_pdm(self) -> bool:
        """Whether or not the board supports PDM audio input such as a digital microphone.
        
        :return: has pdm input support
        :rtype: bool
        """
        return not self.pdm_clock is None and not self.pdm_data is None
    def get_pdm(self, sample_rate:int=None, bit_depth:int=16) -> PDMIn:
        """Get the PDM audio input object, :class:`audiobusio.PDMIn`, if supported by the board.
        
        :return: pdm input object
        :rtype: :class:`audiobusio.PDMIn`
        """
        if not self.has_pdm(): return None
        from audiobusio import PDMIn
        return PDMIn(
            clock_pin=self.pdm_clock,
            data_pin=self.pdm_data,
            sample_rate=sample_rate,
            bit_depth=bit_depth
        )
    
    ttp_sdo:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: TTP229 data pin (SDO) for 2-wire serial output operation.
    """
    ttp_scl:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: TTP229 clock pin (SCL) for 2-wire serial output operation.
    """
    ttp_mode:str = "TTP16"
    """str: The mode for TTP229 communication. Either 16 keys, "TTP16", or 8 keys, "TTP8".
    """
    def has_ttp(self) -> bool:
        """Whether or not the board has a TTP229 controller IC for capacitive touch input.

        :return: has TTP229
        :rtype: bool
        """
        return not self.ttp_sdo is None and not self.ttp_scl is None
    def get_ttp(self) -> tuple[DigitalInOut]:
        """Get the pins needed to communicate with TTP229 if supported by the board. Returns a tuple of (sdo, scl).

        :return: TTP pins
        :rtype: tuple[:class:`digitalio.DigitalInOut`]
        """
        if not self.has_ttp(): return None
        sdo = DigitalInOut(self.ttp_sdo)
        sdo.direction = Direction.INPUT
        sdo.pull = Pull.UP
        scl = DigitalInOut(self.ttp_scl)
        scl.direction = Direction.OUTPUT
        return (sdo, scl)
    def get_ttp_mode(self) -> str:
        """Get the TTP229 mode supported by the board. Currently, "TTP8" (8 keys) and "TTP16" (16 keys) are supported.

        :return: ttp mode
        :rtype: str
        """
        return self.ttp_mode # "TTP8" or "TTP16"
    
    touch_keys:list[microcontroller.Pin] = None
    """list[:class:`microcontroller.Pin`]: The pins that are used for capacitive touch input in ascending order.
    """
    def has_touch_keys(self) -> bool:
        """Whether or not the board has any direct capacitive touch inputs.
        
        :return: has capacitive touch input
        :rtype: bool
        """
        return not self.touch_keys is None and len(self.touch_keys) > 0
    def get_touch_keys(self) -> list[microcontroller.Pin]:
        """Get all capacitive touch input pins if supported by the board.
        
        :return: touch input pins
        :rtype: list[microcontroller.Pin]
        """
        return self.touch_keys
    
    spi_clock:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: SPI clock pin used for SD card operation.
    """
    spi_mosi:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: SPI master out slave in (MOSI) pin used for SD card operation.
    """
    spi_miso:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: SPI master in slave out (MISO) pin used for SD card operation.
    """
    spi_cs:microcontroller.Pin = None
    """:class:`microcontroller.Pin`: SPI chip select (CS) pin used for SD card operation.
    """
    def has_spi(self) -> bool:
        """Whether or not the board supports SPI communication, excluding chip select (CS).

        :return: has spi pins
        :rtype: bool
        """
        return not self.spi_clock is None and not self.spi_mosi is None and not self.spi_miso is None
    def get_spi(self) -> SPI:
        """Get the :class:`busio.SPI` object for the board if supported.

        :return: spi object
        :rtype: :class:`busio.SPI`
        """
        if not self.has_spi(): return None
        from busio import SPI
        return SPI(
            clock=self.spi_clock,
            MOSI=self.spi_mosi,
            MISO=self.spi_miso
        )
    def has_spi_cs(self) -> bool:
        """Whether or not the board has a chip select pin for SPI communication with SD card storage.
        
        :return: has spi chip select
        :rtype: bool
        """
        return self.has_spi() and not self.spi_cs is None
    def get_spi_cs(self) -> microcontroller.Pin:
        """Get the chip select pin used for SPI communication with SD card storage if supported.
        
        :return: chip select pin
        :rtype: :class:`microcontroller.Pin`
        """
        return self.spi_cs
    def has_sd_card(self) -> bool:
        """Whether or not the board has the necessary hardware to support SD card storage via SPI communcation.
        
        :return: has sd card
        :rtype: bool
        """
        return self.has_spi() and self.has_spi_cs()
    def get_sd_card(self) -> sdcardio.SDCard:
        """Get the sd card object to manage SD card storage if supported by the board.
        
        :return: sd card
        :rtype: :class:`sdcardio.SDCard`
        """
        if not self.has_sd_card(): return None
        import sdcardio
        return sdcardio.SDCard(self.get_spi(), self.get_spi_cs())
    def mount_sd_card(self, path="/sd") -> bool:
        """Mount the sd card at the designated path if supported. All necessary hardware and file system objects will be generated during this operation. If the board does not support SD card storage, this method will return False.

        :param path: The absolute path at which to mount the sd card in the CircuitPython virtual file storage. Defaults to "/sd".
        :type path: str
        :return: sd card mounted
        :rtype: bool
        """
        if not self.has_sd_card(): return False
        sdcard = self.get_sd_card()
        import storage
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, path)
        return True
    
    cpu_freq:int = None
    """int: The frequency (in hz) at which to set the CPU whenever the board is overclocked.
    """
    def can_overclock(self) -> bool:
        """Whether or not the board supports CPU overclocking (by default).

        :return: supports overclock
        :rtype: bool
        """
        return not self.cpu_freq is None
    def overclock(self, freq:int=None) -> bool:
        """Alter the CPU frequency of the board to the desired frequency (in hz). Defaults to frequency designated by the board if left unset. If not supported by the board, returns False. Otherwise, returns whether or not the actual frequency matches the desired frequency after alteration (overclock may still occur regardless).

        :param freq: The desired frequency (in hz) of the overclock. Leave unset to use board's default setting.
        :type freq: int
        :return: If the overclock is supported or actual frequency matches desired frequency.
        :rtype: bool
        """
        if freq is None and not self.cpu_freq is None:
            freq = self.cpu_freq
        elif freq is None:
            return False
        microcontroller.cpu.frequency = freq
        return microcontroller.cpu.frequency == freq

    def bootloader(self):
        """Perform a software reset into the RP2040 bootloader. Useful if BOOTSEL button is inaccessible on board.
        """
        microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
        microcontroller.reset()

class Rev1(Board):
    """First board revision of the pico_synth_sandbox dedicated hardware which can be found on [GitHub](https://github.com/dcooperdalrymple/pico_synth_sandbox-hardware/releases/tag/Rev1). Supports PWM audio output, I2S audio output, Midi UART, 16x2 character lcd, PDM audio input, and 12 direct capacitive touch keys.
    """

    led                 = board.LED

    encoders = [(
                          board.GP1,
                          board.GP0,
                          board.GP2
    )]

    uart_tx             = board.GP4
    uart_rx             = board.GP5

    lcd_rs              = board.GP20
    lcd_en              = board.GP21
    lcd_d4              = board.GP22
    lcd_d5              = board.GP26
    lcd_d6              = board.GP27
    lcd_d7              = board.GP28

    pwm_audio_left      = board.GP16
    pwm_audio_right     = board.GP17

    i2s_out_bit_clock   = board.GP16
    i2s_out_word_select = board.GP17
    i2s_out_data        = board.GP18

    pdm_clock           = board.GP4
    pdm_data            = board.GP5

    touch_keys = [
                          board.GP19,
                          board.GP3,
                          board.GP6,
                          board.GP7,
                          board.GP8,
                          board.GP9,
                          board.GP10,
                          board.GP11,
                          board.GP12,
                          board.GP13,
                          board.GP14,
                          board.GP15
    ]

class Rev2(Board):
    """Second board revision of the pico_synth_sandbox dedicated hardware which can be found on [GitHub](https://github.com/dcooperdalrymple/pico_synth_sandbox-hardware/releases/tag/Rev2). Supports I2S audio output, I2S audio input, Midi UART, 16x2 character lcd, 16 capacitive touch keys with the TTP229, SPI SD card storage, and a 250MHz overclock.
    """

    led                 = board.LED

    encoders = [(
                          board.GP12,
                          board.GP11,
                          board.GP13
    ), (
                          board.GP17,
                          board.GP16,
                          board.GP18
    )]
    
    uart_tx             = board.GP4
    uart_rx             = board.GP5

    lcd_rs              = board.GP7
    lcd_en              = board.GP6
    lcd_d4              = board.GP22
    lcd_d5              = board.GP26
    lcd_d6              = board.GP27
    lcd_d7              = board.GP28

    i2s_out_bit_clock   = board.GP19
    i2s_out_word_select = board.GP20
    i2s_out_data        = board.GP21

    i2s_in_bit_clock    = board.GP8
    i2s_in_word_select  = board.GP9
    i2s_in_data         = board.GP10

    ttp_sdo             = board.GP14
    ttp_scl             = board.GP15
    ttp_mode            = "TTP16"

    spi_clock           = board.GP2
    spi_mosi            = board.GP3
    spi_miso            = board.GP0
    spi_cs              = board.GP1

    cpu_freq            = 250000000

def get_board(name:str=None, overclock:bool=True) -> Board:
    """Get the current board as designated by the `settings.toml` file or directly via the name parameter. If not valid board identifier is set, will return an empty :class:`pico_synth_sandbox.board.Board` object.

    :param name: The identifier name of the desired board. Leave unset to use the value defined in `settings.toml` as BOARD. Possible values are "Rev1" or "Rev2".
    :type name: str
    :param overclock: Whether or not to perform the default CPU overclock on initialization if supported by the board.
    :type overclock: bool
    :return: the board object
    :rtype: :class:`pico_synth_sandbox.board.Board`
    """
    if name is None:
        name = os.getenv("BOARD", "Rev2")
    if name == "Rev2":
        return Rev2(overclock)
    elif name == "Rev1":
        return Rev1(overclock)
    else:
        return Board(overclock)
