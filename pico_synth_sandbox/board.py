# pico_synth_sandbox/board.py
# 2024 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import board, os, microcontroller
from digitalio import DigitalInOut, Direction, Pull

class Board:

    def __init__(self, overclock:bool=True):
        if overclock:
            self.overclock()

    led = None
    def has_led(self):
        return not self.led is None
    def get_led(self):
        if not self.has_led(): return None
        pin = DigitalInOut(self.led)
        pin.direction = Direction.OUTPUT
        return pin
    
    encoders = []
    def has_encoders(self):
        return not self.encoders is None and len(self.encoders) > 0
    def get_encoder(self, index=0):
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
        if not self.has_encoders():
            return None
        encoders = []
        for i in range(len(self.encoders)):
            encoders.append(self.get_encoder(i))
        return encoders
    def num_encoders(self):
        if not self.has_encoders():
            return 0
        return len(self.encoders)

    uart_tx = None
    uart_rx = None
    def has_uart(self):
        return not self.uart_tx is None and not self.uart_rx is None
    def get_uart(self, baudrate=31250):
        if not self.has_uart(): return None
        from busio import UART
        return UART(
            tx=self.uart_tx,
            rx=self.uart_rx,
            baudrate=baudrate,
            timeout=0.001
        )

    lcd_rs = None
    lcd_en = None
    lcd_d4 = None
    lcd_d5 = None
    lcd_d6 = None
    lcd_d7 = None
    def get_lcd(self, columns=16, rows=2):
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
    
    pwm_out_left = None
    pwm_out_right = None
    def has_pwm_out(self):
        return not self.pwm_out_left is None and not self.pwm_out_right is None
    def get_pwm_out(self):
        if not self.has_pwm_out(): return None
        from audiopwmio import PWMAudioOut
        return PWMAudioOut(
            left_channel=self.pwm_out_left,
            right_channel=self.pwm_out_right
        )
    
    i2s_out_bit_clock = None
    i2s_out_word_select = None
    i2s_out_data = None
    def has_i2s_out(self):
        return not self.i2s_out_bit_clock is None and not self.i2s_out_word_select is None and not self.i2s_out_data is None
    def get_i2s_out(self):
        if not self.has_i2s_out(): return None
        from audiobusio import I2SOut
        return I2SOut(
            bit_clock=self.i2s_out_bit_clock,
            word_select=self.i2s_out_word_select,
            data=self.i2s_out_data
        )
    
    def get_audio_out(self):
        if self.has_i2s_out(): return self.get_i2s_out()
        if self.has_pwm_out(): return self.get_pwm_out()
        return None

    i2s_in_bit_clock = None
    i2s_in_word_select = None
    i2s_in_data = None
    def has_i2s_in(self):
        return not self.i2s_in_bit_clock is None and not self.i2s_in_word_select is None and not self.i2s_in_data is None
    def get_i2s_in(self):
        if not self.has_i2s_in(): return None
        # TODO
        return None
    
    pdm_clock = None
    pdm_data = None
    def has_pdm(self):
        return not self.pdm_clock is None and not self.pdm_data is None
    def get_pdm(self, sample_rate=None, bit_depth=16):
        if not self.has_pdm(): return None
        from audiobusio import PDMIn
        return PDMIn(
            clock_pin=self.pdm_clock,
            data_pin=self.pdm_data,
            sample_rate=sample_rate,
            bit_depth=bit_depth
        )
    
    ttp_sdo = None
    ttp_scl = None
    ttp_mode = "TTP16"
    def has_ttp(self):
        return not self.ttp_sdo is None and not self.ttp_scl is None
    def get_ttp(self):
        if not self.has_ttp(): return None
        sdo = DigitalInOut(self.ttp_sdo)
        sdo.direction = Direction.INPUT
        sdo.pull = Pull.UP
        scl = DigitalInOut(self.ttp_scl)
        scl.direction = Direction.OUTPUT
        return (sdo, scl)
    def get_ttp_mode(self):
        return self.ttp_mode # "TTP8" or "TTP16"
    
    touch_keys = None
    def has_touch_keys(self):
        return not self.touch_keys is None and len(self.touch_keys) > 0
    def get_touch_keys(self):
        return self.touch_keys
    
    spi_clock = None
    spi_mosi = None
    spi_miso = None
    spi_cs = None
    def has_spi(self):
        return not self.spi_clock is None and not self.spi_mosi is None and not self.spi_miso is None
    def get_spi(self):
        if not self.has_spi(): return None
        from busio import SPI
        return SPI(
            clock=self.spi_clock,
            MOSI=self.spi_mosi,
            MISO=self.spi_miso
        )
    def has_spi_cs(self):
        return self.has_spi() and not self.spi_cs is None
    def get_spi_cs(self):
        return self.spi_cs
    def has_sd_card(self):
        return self.has_spi() and self.has_spi_cs()
    def get_sd_card(self):
        if not self.has_sd_card(): return None
        import sdcardio
        return sdcardio.SDCard(self.get_spi(), self.get_spi_cs())
    def mount_sd_card(self, path="/sd"):
        if not self.has_sd_card(): return False
        sdcard = self.get_sd_card()
        import storage
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, path)
        return True
    
    cpu_freq = None
    def can_overclock(self):
        return not self.cpu_freq is None
    def overclock(self, freq:int=None):
        if freq is None and not self.cpu_freq is None:
            freq = self.cpu_freq
        elif freq is None:
            return False
        microcontroller.cpu.frequency = freq
        return microcontroller.cpu.frequency == freq

    def bootloader(self):
        microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
        microcontroller.reset()

class Rev1(Board):
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

    cpu_freq            = 250000000 # 125MHz => 200MHz, causes issues with LCD at 250MHz+

def get_board(name=None, overclock=True):
    if name is None:
        name = os.getenv("BOARD", "Rev2")
    if name == "Rev2":
        return Rev2(overclock)
    elif name == "Rev1":
        return Rev1(overclock)
    else:
        return Board(overclock)
