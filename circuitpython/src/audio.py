class Audio:
    def __init__(self, output, count=1):
        if count < 1: count = 1
        self._rate = os.getenv("AUDIO_RATE", 22050)
        self._size = os.getenv("AUDIO_BUFFER", 2048)
        self._mixer = Mixer(
            voice_count=count,
            sample_rate=self._rate,
            channel_count=2,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=self._size
        )
        self._output = output
        self._output.play(self._mixer)

    def set_level(self, value, index=-1):
        if index < 0:
            for voice in self._mixer.voice:
                voice.level = value
        elif index < len(self._mixer.voice):
            self._mixer.voice[index].level = value

    def play(self, source, index=0):
        if index >= 0 and index < len(self._mixer.voice):
            self._mixer.voice[index].play(source)

    def get_sample_rate(self):
        return self._rate
    def get_buffer_size(self):
        return self._size

class I2SAudio(Audio):
    def __init__(self, count=1):
        Audio.__init__(self, I2SOut(
            bit_clock=board.GP16,
            word_select=board.GP17,
            data=board.GP18
        ), count)

class PWMAudio(Audio):
    def __init__(self, count=1):
        Audio.__init__(self, PWMAudioOut(
            left_channel=board.GP16,
            right_channel=board.GP17
        ), count)

def get_audio_driver(count=1):
    if os.getenv("AUDIO_DRIVER", "PWM") == "I2S":
        return I2SAudio(count)
    else:
        return PWMAudio(count)
