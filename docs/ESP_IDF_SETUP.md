# ESP-IDF Setup Guide

This guide walks you through installing ESP-IDF (Espressif IoT Development Framework) to build the ESP32 firmware.

## macOS

### Option 1: Quick Install (Recommended)

```bash
# Install prerequisites
brew install cmake ninja dfu-util python3

# Clone ESP-IDF
mkdir -p ~/.espressif
cd ~/.espressif
git clone -b v5.2.2 --recursive https://github.com/espressif/esp-idf.git

# Run install script
cd esp-idf
./install.sh esp32

# Add alias to your shell (add to ~/.zshrc or ~/.bashrc)
echo 'alias get_idf="source ~/.espressif/esp-idf/export.sh"' >> ~/.zshrc
source ~/.zshrc
```

### Option 2: Official Installer

Download from: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/

## Linux (Ubuntu/Debian)

```bash
# Install prerequisites
sudo apt-get update
sudo apt-get install git wget flex bison gperf python3 python3-pip \
    python3-venv cmake ninja-build ccache libffi-dev libssl-dev \
    dfu-util libusb-1.0-0

# Clone ESP-IDF
mkdir -p ~/esp
cd ~/esp
git clone -b v5.2.2 --recursive https://github.com/espressif/esp-idf.git

# Install
cd esp-idf
./install.sh esp32

# Add to bashrc
echo 'alias get_idf=". $HOME/esp/esp-idf/export.sh"' >> ~/.bashrc
source ~/.bashrc
```

## Windows

1. Download the ESP-IDF Tools Installer from:
   https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/windows-setup.html

2. Run the installer and follow prompts

3. Use "ESP-IDF Command Prompt" from Start Menu for all commands

## Verify Installation

```bash
# Activate ESP-IDF environment
get_idf

# Check version
idf.py --version
# Should output: ESP-IDF v5.x.x
```

## Building the Firmware

```bash
# Navigate to firmware directory
cd esp32-airtag-tracker/firmware

# Activate ESP-IDF
get_idf

# Build
idf.py build

# Flash (replace PORT with your device)
idf.py -p /dev/cu.usbserial-XXX flash

# Or use the provided script
./flash_esp32.sh -p /dev/cu.usbserial-XXX
```

## Finding Your ESP32's Port

### macOS
```bash
ls /dev/cu.usb*
# Usually: /dev/cu.usbserial-XXXX or /dev/cu.SLAB_USBtoUART
```

### Linux
```bash
ls /dev/ttyUSB*
# Usually: /dev/ttyUSB0
```

### Windows
Check Device Manager → Ports (COM & LPT)
Usually: COM3, COM4, etc.

## Troubleshooting

### "Permission denied" on Linux
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### "Failed to connect" error
- Hold BOOT button while starting flash
- Try a different USB cable (data cable, not charge-only)
- Check if correct port is selected

### Build fails with missing dependencies
```bash
# Re-run the install script
cd ~/.espressif/esp-idf  # or wherever you installed
./install.sh esp32
get_idf
```
