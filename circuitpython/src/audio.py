class Audio:
    def __init__(self, output):
        self._mixer = Mixer(
            voice_count=1,
            sample_rate=os.getenv("AUDIO_RATE", 22050),
            channel_count=2,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=os.getenv("AUDIO_BUFFER", 2048)
        )
        self._output = output
        self._output.play(self._mixer)

    def set_level(self, value):
        self._mixer.voice[0].level = value

    def play(self, source):
        self._mixer.voice[0].play(source)

class I2SAudio(Audio):
    def __init__(self):
        Audio.__init__(I2SOut(
            bit_clock=board.GP17,
            word_select=board.GP18,
            data=board.GP19
        ))

class PWMAudio(Audio):
    def __init__(self):
        Audio.__init__(PWMAudioOut(
            left_channel=board.GP17,
            right_channel=board.GP18
        ))
