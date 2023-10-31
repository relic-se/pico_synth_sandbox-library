DEVICE := /media/$(USER)/CIRCUITPY/
ifeq ($(wildcard $(DEVICE).),)
	DEVICE := /run/media/$(USER)/CIRCUITPY/
endif

MPYCROSS = ./bin/mpy-cross

SRCDIR = ./src

LIB = pico_synth_sandbox
LIB_SRCS := \
	$(SRCDIR)/import.py \
	$(SRCDIR)/global.py \
	$(SRCDIR)/display.py \
	$(SRCDIR)/encoder.py \
	$(SRCDIR)/audio.py \
	$(SRCDIR)/midi.py \
	$(SRCDIR)/keyboard.py \
	$(SRCDIR)/touch-keyboard.py \
	$(SRCDIR)/timer.py \
	$(SRCDIR)/arpeggiator.py \
	$(SRCDIR)/sequencer.py \
	$(SRCDIR)/waveform.py \
	$(SRCDIR)/synth.py \
	$(SRCDIR)/voice.py \
	$(SRCDIR)/voices/oscillator.py \
	$(SRCDIR)/voices/drum.py \
	$(SRCDIR)/voices/sample.py \
	$(SRCDIR)/microphone.py
LIB_PY = ./$(LIB).py
LIB_MPY = ./$(LIB).mpy

SRCS := boot.py $(LIB_MPY)
SETTINGS = settings.toml
SAMPLES_DIR = ./samples
SAMPLES := $(shell find $(SAMPLES_DIR) -type f)

all: upload

upload: clean $(LIB_MPY) src lib settings samples

update: clean $(LIB_MPY) src lib

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
	circup install -r requirements.txt

settings:
	@echo $(SETTINGS) "=>" $(DEVICE)$(SETTINGS)
	@cp $(SETTINGS) $(DEVICE)$(SETTINGS)

samples:
	@mkdir $(DEVICE)$(SAMPLES_DIR) || true
	@for file in $(SAMPLES) ; do \
		echo $${file} "=>" $(DEVICE)$${file} ; \
		cp $${file} $(DEVICE)$${file} ; \
	done
