# Global Constants

log2 = math.log(2) # for octave conversion

# Global Functions

def free_module(mod):
    if type(mod) is tuple:
        for _mod in mod:
            free_module(_mod)
    else:
        name = mod.__name__
        if name in sys.modules:
            del sys.modules[name]
        gc.collect()
def free_all_modules():
    for name in sys.modules:
        del sys.modules[name]
    gc.collect()

def check_dir(path):
    try:
        os.stat(path)
    except:
        os.mkdir(path)

def getenvgpio(key, default=None):
    return getattr(board, os.getenv(key, default), None)

def getenvfloat(key, default=0.0, decimals=2):
    mod=math.pow(10.0,decimals*1.0)
    return os.getenv(key, default*mod)/mod

def getenvbool(key, default=False):
    default = 1 if default else 0
    return os.getenv(key, 1 if default else 0) > 0

def truncate_str(value, length, right_aligned=False):
    if not type(value) is str:
        value = str(value)
    if len(value) > length:
        value = value[:length]
    elif len(value) < length:
        if right_aligned:
            value = " " * (length - len(value)) + value
        else:
            value = value + " " * (length - len(value))
    return value

def clamp(value, minimum=0.0, maximum=1.0):
    return min(max(value, minimum), maximum)

def map_value(value, minimum, maximum):
    return clamp(value) * (maximum - minimum) + minimum
def unmap_value(value, minimum, maximum):
    return (clamp(value, minimum, maximum) - minimum) / (maximum - minimum)

def is_pow2(value):
    value = math.log(value)/log2
    return math.ceil(value) == math.floor(value)

def fft(data, log=True, dtype=numpy.int16, length=1024):
    if len(data) > length:
        offset = (len(data)-length)//2
        data = data[offset:len(data)-offset]

    if dtype is numpy.uint16:
        mean = int(numpy.mean(data))
        data = numpy.array([x - mean for x in data], dtype=numpy.int16)

    # Ensure that data length is a power of 2
    if len(data) < 2:
        return None
    if not is_pow2(len(data)):
        j = 2
        while True:
            j *= 2
            if j > len(data):
                data = data[:int(j//2)]
                break

    data = ulab.utils.spectrogram(data)
    data = data[1:(len(data)//2)-1]
    if log:
        data = numpy.log(data)
    gc.collect()
    return data

def fftfreq(data, sample_rate=None, dtype=numpy.int16):
    if sample_rate is None:
        sample_rate = Audio.get_sample_rate()
    data = fft(data, log=False, dtype=dtype)
    freq = numpy.argmax(data) / len(data) * sample_rate / 4
    del data
    gc.collect()
    return freq
