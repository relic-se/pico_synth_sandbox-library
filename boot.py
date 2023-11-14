# pico_synth_sandbox - boot.py
# 2023 Cooper Dalrymple - me@dcdalrymple.com
# GPL v3 License
# Version 0.1

import gc, os
import storage, usb_hid, usb_cdc
import usb_midi
from pico_synth_sandbox import free_module, check_dir

# Disable write protection and unnecessary usb features
storage.remount("/", False, disable_concurrent_write_protection=True)
usb_hid.disable()
usb_cdc.enable(console=True, data=False)
free_module((storage, usb_hid, usb_cdc))

# Create directories
check_dir("/samples")

# Configure USB Midi
if os.getenv("MIDI_USB", 0) > 0:
    usb_midi.enable()
else:
    usb_midi.disable()

gc.collect()
