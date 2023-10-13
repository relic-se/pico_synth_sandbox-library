class Waveform:

    @staticmethod
    def get_samples():
        return os.getenv("WAVE_SAMPLES", 256)

    @staticmethod
    def get_amplitude():
        return os.getenv("WAVE_AMPLITUDE", 12000)

    @staticmethod
    def get_saw():
        if not hasattr(Waveform, "_saw"):
            Waveform._saw = numpy.linspace(Waveform.get_amplitude(), -Waveform.get_amplitude(), num=Waveform.get_samples(), dtype=numpy.int16)
        return Waveform._saw

    @staticmethod
    def _get_sine(offset=0.0):
        return numpy.array(numpy.sin(numpy.linspace(offset*numpy.pi, (2+offset)*numpy.pi, Waveform.get_samples(), endpoint=False)) * Waveform.get_amplitude(), dtype=numpy.int16)

    @staticmethod
    def get_sine():
        if not hasattr(Waveform, "_sine"):
            Waveform._sine = Waveform._get_sine()
        return Waveform._sine

    @staticmethod
    def get_offset_sine():
        if not hasattr(Waveform, "_offset_sine"):
            Waveform._offset_sine = Waveform._get_sine(0.5)
        return Waveform._offset_sine

    @staticmethod
    def get_square():
        if not hasattr(Waveform, "_square"):
            Waveform._square = numpy.concatenate((numpy.ones(Waveform.get_samples()//2, dtype=numpy.int16)*Waveform.get_amplitude(),numpy.ones(Waveform.get_samples()//2, dtype=numpy.int16)*-Waveform.get_amplitude()))
        return Waveform._square

    @staticmethod
    def get_noise():
        if not hasattr(Waveform, "_noise"):
            Waveform._noise = numpy.array([random.randint(-Waveform.get_amplitude(), Waveform.get_amplitude()) for i in range(Waveform.get_samples())], dtype=numpy.int16)
        return Waveform._noise

    @staticmethod
    def get_sine_noise():
        if not hasattr(Waveform, "_sine_noise"):
            Waveform.get_sine()
            Waveform.get_noise()
            Waveform._sine_noise = numpy.array([int(max(min(Waveform._sine[i] + (Waveform._noise[i]/2.0), Waveform.get_amplitude()), -Waveform.get_amplitude())) for i in range(Waveform.get_samples())], dtype=numpy.int16)
        return Waveform._sine_noise

    @staticmethod
    def get_offset_sine_noise():
        if not hasattr(Waveform, "_offset_sine_noise"):
            Waveform.get_offset_sine()
            Waveform.get_noise()
            Waveform._offset_sine_noise = numpy.array([int(max(min(Waveform._offset_sine[i] + (Waveform._noise[i]/2.0), Waveform.get_amplitude()), -Waveform.get_amplitude())) for i in range(Waveform.get_samples())], dtype=numpy.int16)
        return Waveform._offset_sine_noise
