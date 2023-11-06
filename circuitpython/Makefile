DEVICE := /media/$(USER)/CIRCUITPY/
ifeq ($(wildcard $(DEVICE).),)
	DEVICE := /run/media/$(USER)/CIRCUITPY/
endif

MPYCROSS = ./bin/mpy-cross

LIB_ROOT = pico_synth_sandbox
LIB_SRCS := \
	$(LIB_ROOT)/__init__ \
	$(LIB_ROOT)/display \
	$(LIB_ROOT)/encoder \
	$(LIB_ROOT)/audio \
	$(LIB_ROOT)/midi \
	$(LIB_ROOT)/keyboard/__init__ \
	$(LIB_ROOT)/keyboard/touch \
	$(LIB_ROOT)/timer \
	$(LIB_ROOT)/arpeggiator \
	$(LIB_ROOT)/sequencer \
	$(LIB_ROOT)/waveform \
	$(LIB_ROOT)/synth \
	$(LIB_ROOT)/voice/__init__ \
	$(LIB_ROOT)/voice/oscillator \
	$(LIB_ROOT)/voice/drum \
	$(LIB_ROOT)/voice/sample \
	$(LIB_ROOT)/microphone
LIB_MPY = $(LIB_SRCS:%=%.mpy)

SRCS := boot.py
SETTINGS = settings.toml
SAMPLES_DIR = ./samples
SAMPLES := $(shell find $(SAMPLES_DIR) -type f)

all: upload

upload: clean $(LIB_MPY:%=./%) src lib requirements settings samples

update: clean $(LIB_MPY:%=./%) src lib requirements

compile: clean $(LIB_MPY:%=./%)

clean:
	@rm $(LIB_MPY) || true

%.mpy: %.py
	$(MPYCROSS) -o $@ $<

src: $(SRCS)
	@for file in $^ ; do \
		echo $${file} "=>" $(DEVICE)$${file} ; \
		cp $${file} $(DEVICE)$${file} ; \
	done

lib: $(LIB_MPY)
	@mkdir $(DEVICE)lib/$(LIB_ROOT) || true
	@mkdir $(DEVICE)lib/$(LIB_ROOT)/keyboard || true
	@mkdir $(DEVICE)lib/$(LIB_ROOT)/voice || true
	@for file in $^ ; do \
		echo ./$${file} "=>" $(DEVICE)lib/$${file} ; \
		cp ./$${file} $(DEVICE)lib/$${file} ; \
	done

requirements:
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
