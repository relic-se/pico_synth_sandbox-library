DEVICE = /media/$(USER)/CIRCUITPY/
MPYCROSS = ./bin/mpy-cross

SRCDIR = ./src

LIB = pico_synth_sandbox
LIB_SRCS := $(SRCDIR)/import.py $(SRCDIR)/global.py $(SRCDIR)/display.py $(SRCDIR)/encoder.py $(SRCDIR)/audio.py $(SRCDIR)/midi.py $(SRCDIR)/keyboard.py $(SRCDIR)/touch-keyboard.py $(SRCDIR)/arpeggiator.py
LIB_PY = ./$(LIB).py
LIB_MPY = ./$(LIB).mpy

SRCS := settings.toml boot.py code.py $(LIB_MPY)

all: upload

upload: clean $(LIB_MPY) src lib

update: clean $(LIB_MPY) src

compile: clean $(LIB_MPY)

clean:
	@rm $(LIB_PY) || true
	@rm $(LIB_MPY) || true

$(LIB_PY):
	cat $(LIB_SRCS) >> $@

$(LIB_MPY): $(LIB_PY)
	$(MPYCROSS) -o $@ $<

src: $(SRCS)
	@for file in $^ ; do \
		echo $${file} "=>" $(DEVICE)$${file} ; \
		cp $${file} $(DEVICE)$${file} ; \
	done

lib:
	circup update
