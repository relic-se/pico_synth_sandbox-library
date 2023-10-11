class Waveform:

    def get_samples():
        return os.getenv("WAVE_SAMPLES", 256)
    def get_amplitude():
        return os.getenv("WAVE_AMPLITUDE", 12000)
    
    def get_saw():
        return numpy.linspace(Waveform.get_amplitude(), -Waveform.get_amplitude(), num=Waveform.get_samples(), dtype=numpy.int16)
    
    def get_sine():
        return numpy.array(numpy.sin(numpy.linspace(0, 2*numpy.pi, Waveform.get_samples(), endpoint=False)) * Waveform.get_amplitude(), dtype=numpy.int16)
    
    def get_square():
        return numpy.concatenate((numpy.ones(Waveform.get_samples()//2, dtype=numpy.int16)*Waveform.get_amplitude(),numpy.ones(Waveform.get_samples()//2, dtype=numpy.int16)*-Waveform.get_amplitude()))

    def get_noise():
        return numpy.array([random.randint(-Waveform.get_amplitude(), Waveform.get_amplitude()) for i in range(Waveform.get_samples())], dtype=numpy.int16)
