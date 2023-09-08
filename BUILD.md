# pico_synth_sandbox Build Guide

## Bill of Materials
The included DigiKey lists separate each aspect of the pico_synth_sandbox into different categories depending on which features you would like to use. Parts have been selected for (nearly) each component. It is not necessary that materials be purchased from DigiKey or be the exact parts listed (especially for passive components).

_The Alpha RD902F-40-00D cannot be sourced from DigiKey and must instead be purchased from a different supplier._

| List | Notes |
|------|-------|
| [Complete](https://www.digikey.com/en/mylists/list/YZL3EKC4RV) | Includes all components for this device. Not recommended because not all features can be used simultaneously. |
| [Main](https://www.digikey.com/en/mylists/list/VQP05S2DJM) | Includes Pico, display, controls, and audio output. |
| [I2S Audio](https://www.digikey.com/en/mylists/list/779CKTBWFG) | Includes all of the components necessary to integrate I2S audio directly on the board. A PCM5102A module can be used instead. |
| [PWM Audio](https://www.digikey.com/en/mylists/list/15CELMUPXG) | Includes all of the components necessary to support PWM audio. |
| [Midi](https://www.digikey.com/en/mylists/list/VEMJL7VN7M) | Includes all of the components for midi input & output support. If using microphone PDM input, this feature is not supported. |
| [Microphone](https://www.digikey.com/en/mylists/list/MI7EB854OR) | Includes all of the components for PDM audio support. Midi IO is not available if using this feature. |
| [Battery](https://www.digikey.com/en/mylists/list/3WZXO5RL1P) | Support on-board battery charging. |

> For instance, if you would like to have your pico_synth_sandbox work with microphone input, use pwm audio, and be battery powered, you would need to source the components from the following lists: Main, PWM Audio, Microphone, and Battery.

_Solder jumpers will need to be set depending on your configuration. By default, the pico_synth_sandbox Rev1 pcb is set up for I2S Audio and Midi I/O. The necessary jumpers will be defined in the corresponding guide sections below._

### PCB
_PCBs will be available for direct purchase in the future. Until then, PCBs can be ordered directly from a manufacturer using the included KiCad project files._

## Soldering Guide

### Main
**TODO**

### I2S Audio
**TODO**

### PWM Audio
**TODO**

### Midi
**TODO**

### Microphone
**TODO**

### Battery
**TODO**
