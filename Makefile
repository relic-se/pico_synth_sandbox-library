DEVICE := /media/$(USER)/CIRCUITPY/
ifeq ($(wildcard $(DEVICE).),)
	DEVICE := /run/media/$(USER)/CIRCUITPY/
endif

MPYCROSS = ./bin/mpy-cross

LIB = pico_synth_sandbox
LIB_SRCS := \
	__init__ \
	tasks \
	board \
	display \
	encoder \
	audio \
	midi \
	keyboard/__init__ \
	keyboard/touch \
	keyboard/ton_touch \
	timer \
	arpeggiator \
	sequencer \
	waveform \
	synth \
	voice/__init__ \
	voice/oscillator \
	voice/drum \
	voice/sample \
	microphone \
	menu
LIB_MPY = $(LIB_SRCS:%=$(LIB)/%.mpy)

SRCS := boot.py
SETTINGS = settings.toml
SAMPLES_DIR = ./samples
SAMPLES := $(shell find $(SAMPLES_DIR) -type f)

all: package

compile: clean $(LIB_MPY:%=./%)

upload: compile src lib requirements settings samples

update: compile src lib requirements

package: compile zip

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
	@mkdir $(DEVICE)lib/$(LIB) || true
	@mkdir $(DEVICE)lib/$(LIB)/keyboard || true
	@mkdir $(DEVICE)lib/$(LIB)/voice || true
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

zip:
	zip ./$(LIB).zip $(LIB_MPY:%=./%)
