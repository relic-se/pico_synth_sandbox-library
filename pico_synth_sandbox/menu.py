# pico_synth_sandbox/menu.py
# 2024 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License

import os, json, math
import ulab.numpy as numpy
from typing import Callable
from pico_synth_sandbox import clamp, map_value, unmap_value, check_dir, get_filter_frequency_range
from pico_synth_sandbox.display import Display
from pico_synth_sandbox.voice import Voice, AREnvelope
from pico_synth_sandbox.voice.oscillator import Oscillator
import pico_synth_sandbox.waveform as waveform

def apply_value(items:tuple, method:Callable|str, offset:float=0.0) -> Callable:
    if type(method) is str:
        method = getattr(type(items[0]), method)
    if offset > 0.0:
        return lambda value : [method(items[i], value+offset*(i-(len(items)-1)/2)) for i in range(len(items))]
    else:
        return lambda value : [method(items[i], value) for i in range(len(items))]

class MenuItem:
    def __init__(self, title:str="", group:str="", update:Callable=None):
        self._title = title
        self._group = group
        self._update = update
        self._enabled = False
        self._title_enabled = True
    def get_title(self) -> str:
        return self._title
    def get_group(self) -> str:
        return self._group
    def get(self):
        return None
    def get_data(self):
        return None
    def get_label(self) -> str:
        return ""
    def set(self, value):
        pass
    def set_data(self, value):
        self.set(value)
    def disable_title(self):
        self._title_enabled = False
    def navigate(self, step:int) -> bool:
        return True # Indicate to move on to another item
    def previous(self) -> bool:
        return self.navigate(-1)
    def next(self) -> bool:
        return self.navigate(1)
    def increment(self) -> bool:
        return False # Indicate whether to redraw
    def decrement(self) -> bool:
        return False # Indicate whether to redraw
    def reset(self) -> bool:
        return False # Indicate whether to redraw
    def is_enabled(self) -> bool:
        return self._enabled
    def enable(self, display:Display):
        self._enabled = True
        if self._title_enabled:
            title = ""
            if self._group:
                title += self._group
                if self._title: title += ":"
            if self._title:
                title += self._title
            if title:
                display.write(title)
        self.set_cursor_position(display)
    def disable(self):
        self._enabled = False
    def draw(self, display:Display):
        display.write(self.get_label(), (0,1))
    def get_cursor_position(self) -> tuple:
        return (0,1)
    def set_cursor_position(self, display:Display):
        display.set_cursor_position(self.get_cursor_position())
    def set_update(self, callback:Callable):
        self._update = callback
    def _do_update(self):
        if self._update: self._update(self.get())
    
class IntMenuItem(MenuItem):
    def __init__(self, title:str="", group:str="", step:int=1, initial:int=0, minimum:int=0, maximum:int=1, loop:bool=False, sign:bool=False, update:Callable=None):
        MenuItem.__init__(self, title, group, update)
        self._step = step
        self._initial = initial
        self._value = initial
        self._minimum = minimum
        self._maximum = maximum
        self._loop = loop
        self._sign = sign
    def get(self) -> int:
        return self._value
    def get_relative(self) -> float:
        return unmap_value(self._value, self._minimum, self._maximum)
    def get_data(self) -> int:
        return self._value
    def get_label(self) -> str:
        if self._sign:
            return "{:+d}".format(self.get()).replace("+0", "0")
        else:
            return "{:d}".format(self.get())
    def set(self, value:int):
        if not type(value) is int:
            return
        value = clamp(value, self._minimum, self._maximum)
        if self._value != value:
            self._value = value
            self._do_update()
    def increment(self) -> bool:
        if self._value == self._maximum:
            if self._loop:
                self._value = self._minimum
            else:
                return False
        else:
            self._value = min(self._value + self._step, self._maximum)
        self._do_update()
        return True
    def decrement(self) -> bool:
        if self._value == self._minimum:
            if self._loop:
                self._value = self._maximum
            else:
                return False
        else:
            self._value = max(self._value - self._step, self._minimum)
        self._do_update()
        return True
    def reset(self) -> bool:
        if self._value == self._initial:
            return False
        self._value = self._initial
        return True

class NumberMenuItem(MenuItem):
    def __init__(self, title:str="", group:str="", step:float=0.1, initial:float=0.0, minimum:float=0.0, maximum:float=1.0, smoothing:float=1.0, loop:bool=False, update:Callable=None):
        MenuItem.__init__(self, title, group, update)
        self._step = step
        self._initial = initial
        self._value = initial
        self._minimum = minimum
        self._maximum = maximum
        self._smoothing = smoothing
        self._loop = loop
    def has_smoothing(self) -> bool:
        return self._smoothing != 1.0
    def get(self) -> float:
        if self.has_smoothing():
            return map_value(math.pow(self._value, self._smoothing), self._minimum, self._maximum)
        else:
            return self._value
    def get_relative(self) -> float:
        if self.has_smoothing():
            return self._value
        else:
            return unmap_value(self._value, self._minimum, self._maximum)
    def get_data(self) -> float:
        return self._value
    def get_label(self) -> str:
        return self._value
    def set(self, value:float):
        if not type(value) is float:
            return
        if self.has_smoothing():
            value = clamp(value, 0.0, 1.0)
        else:
            value = clamp(value, self._minimum, self._maximum)
        if self._value != value:
            self._value = value
            self._do_update()
    def increment(self) -> bool:
        minimum = 0.0 if self.has_smoothing() else self._minimum
        maximum = 1.0 if self.has_smoothing() else self._maximum
        if self._value == maximum:
            if self._loop:
                self._value = minimum
            else:
                return False
        else:
            self._value = min(self._value + self._step, maximum)
        self._do_update()
        return True
    def decrement(self) -> bool:
        minimum = 0.0 if self.has_smoothing() else self._minimum
        maximum = 1.0 if self.has_smoothing() else self._maximum
        if self._value == minimum:
            if self._loop:
                self._value = maximum
            else:
                return False
        else:
            self._value = max(self._value - self._step, minimum)
        self._do_update()
        return True
    def reset(self) -> bool:
        if self._value == self._initial:
            return False
        self._value = self._initial
        return True

class BooleanMenuItem(IntMenuItem):
    def __init__(self, title:str="", group:str="", initial:bool=False, loop:bool=False, update:Callable=None, true_label:str="On", false_label:str="Off"):
        IntMenuItem.__init__(self, title, group, initial=int(initial), loop=loop, update=update)
        self._true_label=true_label
        self._false_label=false_label
    def get(self) -> bool:
        return bool(self._value)
    def get_label(self) -> str:
        return self._true_label if self.get() else self._false_label

class TimeMenuItem(NumberMenuItem):
    def __init__(self, title:str="", group:str="", step:float=0.025, initial:float=0.0, minimum:float=0.001, maximum:float=4.0, smoothing:float=3.0, update:Callable=None):
        NumberMenuItem.__init__(self, title, group,
            step=step,
            initial=initial,
            minimum=minimum,
            maximum=maximum,
            smoothing=smoothing,
            loop=False,
            update=update
        )
    def get_label(self) -> str:
        return "{:.1f}s".format(self.get()).replace("0.", ".")

class BarMenuItem(NumberMenuItem):
    def __init__(self, title:str="", group:str="", step:float=1/16, initial:float=0.0, minimum:float=0.0, maximum:float=1.0, smoothing:float=1.0, update:Callable=None):
        NumberMenuItem.__init__(self, title, group, step, initial, minimum, maximum, smoothing, False, update)
    def enable(self, display:Display):
        display.enable_horizontal_graph()
        NumberMenuItem.enable(self, display)
    def draw(self, display:Display):
        self.draw_bar(display)
        self.set_cursor_position(display)
    def draw_bar(self, display:Display, position=(0,1), length=16, centered=False):
        minimum = 0.0 if self.has_smoothing() else self._minimum
        maximum = 1.0 if self.has_smoothing() else self._maximum
        display.write_horizontal_graph(self._value, minimum, maximum, position, length, centered)
    def get_bar_position(self, x=0, length=16) -> int:
        return x+min(int(length*self.get_relative()),length-1)
    def get_cursor_position(self) -> tuple:
        return (self.get_bar_position(),1)

class ListMenuItem(IntMenuItem):
    def __init__(self, items:tuple[str], title:str="", group:str="", initial:int=0, loop:bool=True, update:Callable=None):
        IntMenuItem.__init__(self, title, group, initial=initial, maximum=len(items)-1, loop=loop, update=update)
        self._items = items
    def get_label(self) -> str:
        return self._items[self.get()]

class WaveformMenuItem(ListMenuItem):
    def __init__(self, group:str="", update:Callable=None):
        ListMenuItem.__init__(
            self,
            items=("SQUR", "SAWT", "TRNGL", "SINE", "NOISE", "SINN"),
            title="Waveform",
            group=group,
            update=update
        )
    def get_waveform(self):
        value = int(self._value)
        if value == 1:
            return waveform.get_saw()
        elif value == 2:
            return waveform.get_triangle()
        elif value == 3:
            return waveform.get_sine()
        elif value == 4:
            return waveform.get_noise()
        elif value == 5:
            return waveform.get_sine_noise()
        else:
            return waveform.get_square()
    def _do_update(self):
        if self._update: self._update(self.get_waveform())
    def enable(self, display:Display):
        ListMenuItem.enable(self, display)
        display.enable_vertical_graph()
    def draw(self, display:Display):
        wave = self.get_waveform()
        periods = 2
        wavelength = 16//periods
        segment = len(wave)//wavelength
        amplitude = waveform.get_amplitude()
        for j in range(periods):
            for i in range(wavelength):
                display.write_vertical_graph(
                    value=numpy.sum(wave[i*segment:(i+1)*segment]) / segment,
                    minimum=-amplitude*11/8,
                    maximum=amplitude,
                    position=(i+j*wavelength,1)
                )
        display.write(
            value=self.get_label(),
            position=(12,0),
            length=4
        )
    def get_cursor_position(self) -> tuple:
        return (12,0)

class MenuGroup(MenuItem):
    def __init__(self, items:tuple[MenuItem], group:str="", loop:bool=False):
        MenuItem.__init__(self, group=group)
        self._items = items
        self._index = 0
        self._loop = loop
        self._assign_group_name()
    def _assign_group_name(self):
        if self._group:
            for item in self._items:
                if not issubclass(type(item), MenuGroup):
                    item._group = self._group
    
    def get_current_item(self) -> MenuItem:
        return self._items[self._index]
    
    def get(self) -> tuple:
        return tuple([item.get() for item in self._items])
    def get_title(self) -> str:
        return self._group
    def get_data(self) -> dict:
        data = {}
        for item in self._items:
            data[item.get_title()] = item.get_data()
        return data
    def get_item_by_title(self, title:str) -> MenuItem:
        for item in self._items:
            if item.get_title() == title:
                return item
        return None
    def set_data(self, data:dict, reset:bool=True):
        if reset:
            self.reset(True)
        for title in data:
            item = self.get_item_by_title(title)
            if item:
                if isinstance(item, MenuGroup):
                    item.set_data(data[title], False)
                else:
                    item.set_data(data[title])
    def set(self, data:dict):
        self.set_data(data)
    def disable_title(self):
        for item in self._items:
            item.disable_title()
    
    def navigate(self, step:int, display:Display, force:bool=False) -> bool:
        if not force and issubclass(type(self.get_current_item()), MenuGroup) and not self.get_current_item().navigate(step, display):
            return False
        if not self._loop and ((step > 0 and self._index + step >= len(self._items)) or (step < 0 and self._index + step < 0)):
            return True
        if force or issubclass(type(self.get_current_item()), MenuGroup) or self.get_current_item().navigate(step):
            self.get_current_item().disable()
            self._index = (self._index + step) % len(self._items)
            if issubclass(type(self.get_current_item()), MenuGroup):
                self.get_current_item().enable(display, False if force else step < 0)
            else:
                self.get_current_item().enable(display)
            self.draw(display)
        return False
    def previous(self, display:Display, force:bool=False) -> bool:
        return self.navigate(-1, display, force)
    def next(self, display:Display, force:bool=False) -> bool:
        return self.navigate(1, display, force)
    def increment(self) -> bool:
        return self.get_current_item().increment()
    def decrement(self) -> bool:
        return self.get_current_item().decrement()
    def reset(self, full:bool=False) -> bool:
        if full:
            for item in self._items:
                if isinstance(item, MenuGroup):
                    item.reset(True)
                else:
                    item.reset()
        else:
            return self.get_current_item().reset()
    
    def enable(self, display:Display, last:bool = False):
        # NOTE: Don't call MenuItem.enable to avoid drawing MenuGroup
        self._enabled = True
        self._index = len(self._items) - 1 if last else 0
        if issubclass(type(self.get_current_item()), MenuGroup):
            self.get_current_item().enable(display, last)
        else:
            self.get_current_item().enable(display)
    def disable(self):
        MenuItem.disable(self)
        self.get_current_item().disable()

    def draw(self, display:Display):
        self.get_current_item().draw(display)
    def get_cursor_position(self) -> tuple:
        return self.get_current_item().get_cursor_position()

CHARACTERS = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!-_#$%&+@~^"
class CharMenuItem(IntMenuItem):
    def __init__(self, title:str="", group:str="", update:Callable=None):
        IntMenuItem.__init__(self, title, group, maximum=len(CHARACTERS)-1, loop=True, update=update)
    def get_label(self) -> str:
        return CHARACTERS[self._value]
    def set(self, value:str):
        if len(value) == 0:
            return
        IntMenuItem.set(self, CHARACTERS.index(value[0]))
    def reset(self):
        IntMenuItem.reset(self)

class StringMenuItem(MenuGroup):
    def __init__(self, group:str="", length:int=16, update:Callable=None):
        self._length = length
        MenuGroup.__init__(self, tuple([CharMenuItem(str(i+1)) for i in range(length)]), group)
    def get_label(self) -> str:
        return "".join([char.get_label() for char in self._items])
    def get_data(self) -> str:
        return self.get_label()
    def set(self, value:str):
        for i in range(min(len(value), self._length)):
            self._items[i].set(value[i])
    def set_data(self, value:str, reset:bool=True):
        if reset:
            self.reset(True)
        self.set(value)
    def draw(self, display:Display):
        MenuItem.draw(self, display)
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        return (self._index,1)

class AREnvelopeMenuGroup(MenuGroup):
    def __init__(self, envelopes:AREnvelope|tuple[AREnvelope], group:str=""):
        envelopes = tuple(envelopes)
        self._attack = TimeMenuItem(
            "Attack",
            update=apply_value(envelopes, AREnvelope.set_attack)
        )
        self._amount = NumberMenuItem(
            "Amount",
            step=0.05,
            update=apply_value(envelopes, AREnvelope.set_amount)
        )
        self._release = TimeMenuItem(
            "Release",
            update=apply_value(envelopes, AREnvelope.set_release)
        )
        MenuGroup.__init__(self, (self._attack, self._amount, self._release), group)
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.enable_vertical_graph()
    def _get_attack_bars(self) -> int:
        return round(map_value(self._attack.get_relative(), 1, 8))
    def _get_release_bars(self) -> int:
        return round(map_value(self._release.get_relative(), 1, 8))
    def _get_amount_bars(self) -> int:
        return 16 - (self._get_attack_bars() + self._get_release_bars())
    def draw(self, display:Display):
        attack_bars = self._get_attack_bars()
        release_bars = self._get_release_bars()
        amount_bars = 16 - (attack_bars + release_bars)
        amount = self._amount.get_relative()
        for i in range(attack_bars):
            display.write_vertical_graph(amount * ((i + 1) / attack_bars), position=(i,1))
        if amount_bars:
            for i in range(amount_bars):
                display.write_vertical_graph(amount, position=(attack_bars+i,1))
        for i in range(release_bars):
            display.write_vertical_graph(amount * ((i + 1) / release_bars), position=(15-i,1))
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        x = 0
        if self._attack.is_enabled():
            x = self._get_attack_bars()/2
        elif self._amount.is_enabled():
            x = self._get_attack_bars() + self._get_amount_bars()/2
        elif self._release.is_enabled():
            x = 16 - self._get_release_bars()/2
        return (round(x),1)

class ADSREnvelopeMenuGroup(MenuGroup):
    def __init__(self, voices:Oscillator|tuple[Oscillator], group:str=""):
        voices = tuple(voices)
        self._attack_time = TimeMenuItem(
            title="Attack",
            update=apply_value(voices, Oscillator.set_envelope_attack_time)
        )
        self._attack_level = NumberMenuItem(
            "Atk Lvl",
            initial=1.0,
            step=0.05,
            update=apply_value(voices, Oscillator.set_envelope_attack_level)
        )
        self._decay_time = TimeMenuItem(
            "Decay",
            update=apply_value(voices, Oscillator.set_envelope_decay_time)
        )
        self._sustain_level = NumberMenuItem(
            "Stn Lvl",
            initial=0.75,
            step=0.05,
            update=apply_value(voices, Oscillator.set_envelope_sustain_level)
        )
        self._release_time = TimeMenuItem(
            "Release",
            update=apply_value(voices, Oscillator.set_envelope_release_time)
        )
        MenuGroup.__init__(self, (
            self._attack_time,
            self._attack_level,
            self._decay_time,
            self._sustain_level,
            self._release_time
        ), group)
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.enable_vertical_graph()
    def _get_attack_bars(self) -> int:
        return round(map_value(self._attack_time.get_relative(), 1, 5))
    def _get_decay_bars(self) -> int:
        return round(map_value(self._decay_time.get_relative(), 1, 5))
    def _get_release_bars(self) -> int:
        return round(map_value(self._release_time.get_relative(), 1, 5))
    def _get_sustain_bars(self) -> int:
        return 16 - (self._get_attack_bars() + self._get_decay_bars() + self._get_release_bars())
    def draw(self, display:Display):
        attack_bars = self._get_attack_bars()
        decay_bars = self._get_decay_bars()
        release_bars = self._get_release_bars()
        sustain_bars = 16 - (attack_bars + decay_bars + release_bars)
        attack_level = self._attack_level.get_relative()
        sustain_level = self._sustain_level.get_relative()
        for i in range(attack_bars):
            display.write_vertical_graph(
                value = attack_level * ((i + 1) / attack_bars),
                position = (i,1)
            )
        for i in range(decay_bars):
            display.write_vertical_graph(
                value = (attack_level - sustain_level) * ((i + 1) / decay_bars) + sustain_level,
                position = (attack_bars+(decay_bars-1-i),1)
            )
        for i in range(attack_bars+decay_bars, attack_bars+decay_bars+sustain_bars):
            display.write_vertical_graph(sustain_level, position=(i,1))
        for i in range(release_bars):
            display.write_vertical_graph(
                value = sustain_level * ((i + 1) / release_bars),
                position = (15-i,1)
            )
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        x = 0
        if self._attack_time.is_enabled():
            x = self._get_attack_bars()/2
        elif self._attack_level.is_enabled():
            x = self._get_attack_bars()
        elif self._decay_time.is_enabled():
            x = self._get_attack_bars()+self._get_decay_bars()/2
        elif self._sustain_level.is_enabled():
            x = self._get_attack_bars()+self._get_decay_bars()+self._get_sustain_bars()/2
        elif self._release_time.is_enabled():
            x = 16 - self._get_release_bars()/2
        return (round(x),1)

class LFOMenuGroup(MenuGroup):
    def __init__(self, update_depth:Callable=None, update_rate:Callable=None, group:str=""):
        self._depth = BarMenuItem(
            "Depth",
            step=1/64,
            maximum=0.5,
            smoothing=2.0,
            update=update_depth
        )
        self._rate = NumberMenuItem(
            "Rate",
            step=0.01, # relative step
            maximum=32.0,
            smoothing=2.0,
            update=update_rate
        )
        MenuGroup.__init__(self, (
            self._depth,
            self._rate
        ), group)
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.enable_horizontal_graph()
    def draw(self, display:Display):
        self._depth.draw_bar(display, (0,1), 10)
        display.write("{:.1f}hz".format(self._rate.get()), position=(10,1), length=6, right_aligned=True)
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        if self.get_current_item() is self._rate:
            return (10,1)
        else:
            return (self._depth.get_bar_position(0,10),1)

class FilterMenuGroup(MenuGroup):
    def __init__(self, voices:Voice|tuple[Voice], group:str=""):
        voices = tuple(voices)
        self._type = ListMenuItem(
            ("LP", "HP", "BP"),
            "Type",
            update=apply_value(voices, Voice.set_filter_type)
        )
        self._frequency = NumberMenuItem(
            "Freq",
            initial=1.0,
            step=0.01,
            smoothing=3.0,
            update=apply_value(voices, Voice.set_filter_frequency)
        )
        self._resonance = BarMenuItem(
            "Reso",
            update=apply_value(voices, Voice.set_filter_resonance)
        )
        MenuGroup.__init__(self, (
            self._type,
            self._frequency,
            self._resonance
        ), group)
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.enable_horizontal_graph()
    def draw(self, display:Display):
        display.write(
            self._type.get_label(),
            position=(0,1),
            length=2
        )
        range = get_filter_frequency_range()
        display.write(
            "{:d}hz".format(int(map_value(self._frequency.get(), range[0], range[1]))),
            position=(2,1),
            length=8,
            right_aligned=True
        )
        self._resonance.draw_bar(display, (10,1), 6)
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        if self.get_current_item() is self._frequency:
            return (2,1)
        elif self.get_current_item() is self._resonance:
            return (self._resonance.get_bar_position(10,6),1)
        else:
            return (0,1)

class MixMenuGroup(MenuGroup):
    def __init__(self, update_level:Callable=None, update_pan:Callable=None, group:str=""):
        self._level = NumberMenuItem(
            "Level",
            initial=1.0,
            step=1/32,
            update=update_level
        )
        self._pan = BarMenuItem(
            "Pan",
            step=1/8,
            minimum=-1.0,
            update=update_pan
        )
        MenuGroup.__init__(self, (
            self._level,
            self._pan
        ), group)
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.enable_horizontal_graph()
        display.write(' L', (7,1), 2) # Space to clear out previous screen
        display.write('R', (15,1), 1)
    def draw(self, display:Display):
        display.write(
            value="-infdb" if self._level.get() == 0.0 else "{:.1f}db".format(math.log(self._level.get())*10.0),
            position=(0,1),
            length=7,
            right_aligned=True
        )
        self._pan.draw_bar(display, (9,1), 6, True)
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        if self.get_current_item() is self._pan:
            return (self._pan.get_bar_position(9,6),1)
        else:
            return (0,1)

class TuneMenuGroup(MenuGroup):
    def __init__(self, update_coarse:Callable=None, update_fine:Callable=None, update_glide:Callable=None, update_bend:Callable=None, group:str=""):
        self._coarse = IntMenuItem(
            "Coarse",
            minimum=-36,
            maximum=36,
            sign=True,
            update=lambda value : update_coarse(value/12.0)
        )
        self._fine = BarMenuItem(
            "Fine",
            step=1/12/5,
            minimum=-1/12,
            maximum=1/12,
            update=update_fine
        )
        self._glide = TimeMenuItem(
            "Glide",
            step=0.05,
            minimum=0.0,
            maximum=2.0,
            update=update_glide
        )
        self._bend = BarMenuItem(
            "Bend",
            step=1/24,
            minimum=-1.0,
            update=update_bend
        )
        MenuGroup.__init__(self, (
            self._coarse,
            self._fine,
            self._glide,
            self._bend
        ), group)
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.enable_horizontal_graph()
        display.write(' -', (3,1), 2) # Extra space to clear out previous screen
        display.write('+', (7,1), 1)
        display.write('-', (12,1), 1)
        display.write('+', (15,1), 1)
    def draw(self, display:Display):
        display.write(
            value=self._coarse.get_label(),
            position=(0,1),
            length=3,
            right_aligned=True
        )
        self._fine.draw_bar(display, (5,1), 2, True)
        display.write(
            value=self._glide.get_label(),
            position=(8,1),
            length=4,
            right_aligned=True
        )
        self._bend.draw_bar(display, (13,1), 2, True)
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        if self.get_current_item() is self._fine:
            return (self._fine.get_bar_position(5,2),1)
        elif self.get_current_item() is self._glide:
            return (8,1)
        elif self.get_current_item() is self._bend:
            return (self._bend.get_bar_position(13,2),1)
        else:
            return (0,1)

class VoiceMenuGroup(MenuGroup):
    def __init__(self, voices:Voice|tuple[Voice], group:str=""):
        voices = tuple(voices)
        MenuGroup.__init__(self, (
            BarMenuItem(
                "Level",
                initial=1.0,
                update=apply_value(voices, "set_level")
            ),
            BarMenuItem(
                "Velocity",
                update=apply_value(voices, Voice.set_velocity_amount)
            ),
            FilterMenuGroup(voices, "Filter")
        ), group)

class OscillatorMenuGroup(MenuGroup):
    def __init__(self, voices:Oscillator|tuple[Oscillator], group:str=""):
        voices = tuple(voices)
        MenuGroup.__init__(self, (
            MixMenuGroup(
                update_level=apply_value(voices, Oscillator.set_level),
                update_pan=apply_value(voices, Oscillator.set_pan),
                group=group
            ),
            TuneMenuGroup(
                update_coarse=apply_value(voices, Oscillator.set_coarse_tune),
                update_fine=apply_value(voices, Oscillator.set_fine_tune, 1/12/16),
                update_glide=apply_value(voices, Oscillator.set_glide),
                update_bend=apply_value(voices, Oscillator.set_pitch_bend_amount),
                group="Tune"
            ),
            WaveformMenuItem(
                update=apply_value(voices, Oscillator.set_waveform)
            ),
            FilterMenuGroup(voices, "Filter"),
            ADSREnvelopeMenuGroup(
                voices,
                group=group+"AEnv"
            ),
            AREnvelopeMenuGroup(
                tuple(voice._filter_envelope for voice in voices),
                group=group+"FEnv"
            ),
            LFOMenuGroup(
                update_depth=apply_value(voices, Oscillator.set_tremolo_depth),
                update_rate=apply_value(voices, Oscillator.set_tremolo_rate, 0.025),
                group=group+"Tremolo"
            ),
            LFOMenuGroup(
                update_depth=apply_value(voices, Oscillator.set_vibrato_depth),
                update_rate=apply_value(voices, Oscillator.set_vibrato_rate, 0.025),
                group=group+"Vibrato"
            ),
            LFOMenuGroup(
                update_depth=apply_value(voices, Oscillator.set_pan_depth),
                update_rate=apply_value(voices, Oscillator.set_pan_rate, 0.025),
                group=group+"Pan"
            ),
            LFOMenuGroup(
                update_depth=apply_value(voices, Oscillator.set_filter_lfo_depth),
                update_rate=apply_value(voices, Oscillator.set_filter_lfo_rate, 0.025),
                group=group+"FltrLFO"
            )
        ), group)

class PatchMenuGroup(MenuGroup):
    def __init__(self, group:str="", count:int=16, update:Callable=None):
        self._patch = IntMenuItem("Index", maximum=count-1, loop=True, update=lambda value: self._do_update())
        self._name = StringMenuItem("Name")
        MenuGroup.__init__(self, (self._patch, self._name), group)
        self.disable_title()
        self.set_update(update)
    def set(self, value:int, force:bool=False):
        if force:
            self._patch.set(value)
    def set_data(self, data:dict, reset:bool=True):
        if reset:
            self.reset(True)
        # Don't set index
        if "Name" in data:
            self._name.set_data(data["Name"], False)
    def get(self) -> int:
        return self._patch.get()
    def get_name(self) -> str:
        return self._name.get()
    def enable(self, display:Display, last:bool = False):
        MenuGroup.enable(self, display, last)
        display.write(self._group, (0,0), 14)
        self.set_cursor_position(display)
    def draw(self, display:Display):
        display.write("{:02d}".format(self._patch.get()+1), position=(14,0), length=2, right_aligned=True)
        self._name.draw(display)
        self.set_cursor_position(display)
    def get_cursor_position(self) -> tuple:
        if self.get_current_item() is self._patch:
            return (14,0)
        else:
            return self._name.get_cursor_position()
    def reset(self, full:bool=False) -> bool:
        if full:
            # Don't reset index
            self._name.reset(True)
        else:
            return self.get_current_item().reset()

class Menu(MenuGroup):
    def __init__(self, items:tuple, group:str = ""):
        MenuGroup.__init__(self, items, loop=True)
        self._group = group # avoids assigning group name

    def write(self, name:str="", dir:str="/presets") -> bool:
        if not name: name = self._group
        if not name: return False

        data = self.get_data()
        if not data: return False

        path = "{}/{}.json".format(dir, name)

        result = False
        try:
            check_dir(dir)
            with open(path, "w") as file:
                json.dump(data, file)
            print("Successfully written JSON file: {}".format(path))
            result = True
        except:
            print("Failed to write JSON file: {}".format(path))
        return result
    
    def read(self, name:str="", dir:str="/presets") -> bool:
        if not name: name = self._group
        if not name: return False

        path = "{}/{}.json".format(dir, name)
        try:
            os.stat(path)
        except:
            print("Failed to read JSON file, doesn't exist: {}".format(path))
            return False

        data = None
        try:
            with open(path, "r") as file:
                data = json.load(file)
            print("Successfully read JSON file: {}".format(path))
        except:
            print("Failed to read JSON file: {}".format(path))

        if not data or not type(data) is dict:
            return False
        
        self.set_data(data)
        return True
