class Microphone:

    def __init__(self):
        # Settings
        self.buffer_size = Microphone.get_buffer_size()
        self.bit_depth = Microphone.get_bit_depth()
        self.trigger_level = Microphone.get_trigger_level()

        # Input & Buffer
        self.input = PDMIn(
            clock_pin=board.GP4,
            data_pin=board.GP5,
            sample_rate=Audio.get_sample_rate(),
            bit_depth=self.bit_depth
        )
        self.buffer = array.array('H', [0] * self.buffer_size)
        self.buffer_data = numpy.frombuffer(self.buffer, dtype=numpy.uint16)
        self.data = numpy.array([0.0 for i in range(self.buffer_size)], dtype=numpy.float)
        self.mean = 0.0
        self.level = 0.0

        # Callbacks
        self._trigger = None
        self._update = None

    def record(self, name, wait=True):
        filepath = "/samples/{}.wav".format(name)
        try:
            os.remove(filepath)
        except:
            pass

        writer = adafruit_wave.open(filepath, mode="wb")
        writer.setframerate(self.input.sample_rate)
        writer.setnchannels(1)
        writer.setsampwidth(int(math.ceil(self.bit_depth/8)))

        # Wait for trigger
        self.update()
        if wait:
            while True:
                if self.level >= self.trigger_level:
                    break
                self.update()
        writer.writeframes(self.data)
        if self._trigger: self._trigger()

        # Continue recording until level is below trigger
        while True:
            self.update()
            if self.level <= self.trigger_level:
                break
            writer.writeframes(self.data)

        writer.close()
        return filepath
    
    def update(self):
        self.fill_buffer()
        self.calculate_mean()
        self.normalize_buffer()
        self.calculate_level()
        if self._update: self._update(self.level)
    def fill_buffer(self, convert=True):
        self.input.record(self.buffer, self.buffer_size)
    def calculate_mean(self):
        self.mean = numpy.mean(self.buffer_data)
    def normalize_buffer(self):
        self.data = numpy.array([(x - self.mean) / 32768.0 for x in self.buffer_data], dtype=numpy.float)
    def calculate_level(self):
        sum = 0
        for x in self.data:
            sum += abs(x)
        self.level = sum / self.buffer_size
    def get_level(self):
        return self.level
    
    def set_trigger_level(self, value):
        self.trigger_level = value

    def set_update(self, callback):
        self._update = callback
    def set_trigger(self, callback):
        self._trigger = callback

    @staticmethod
    def get_buffer_size():
        return os.getenv("MIC_BUFFER", 256)
    
    @staticmethod
    def get_bit_depth():
        return os.getenv("MIC_BITS", 16)
    
    @staticmethod
    def get_trigger_level():
        return os.getenv("MIC_TRIGGER", 0)
