# Bop-It Hardware Controller

This repository contains the hardware design for a Bop-It style controller using the XIAO ESP32-C3. The project includes a KiCad schematic, and supporting documentation.

## Repository Structure
- src: KiCad project files
- Documentation: System diagram, circuit diagram PDF

## Hardware Modules
- XIAO ESP32-C3 microcontroller
- ADXL345 accelerometer
- SSD1306 OLED display
- Rotary encoder
- Two push buttons
- WS2812B LED strip
- Audio amplifier and speaker
- LiPo battery

## Documentation
The system diagram and circuit schematic are available in the Documentation folder.  
Open the KiCad project using the file:
src/bopit_controller.kicad_pro

## Description
The ESP32-C3 is used as the central controller. Peripherals include I2C devices (OLED and ADXL345), digital inputs (rotary encoder and buttons), a WS2812B LED strip, and an audio output stage driven by PWM. All wiring and layout details are included in the KiCad schematic.
