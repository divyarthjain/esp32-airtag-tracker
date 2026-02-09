# ESP32 AirTag Tracker

Build your own AirTag-compatible tracker using an ESP32. This project leverages Apple's Find My network to locate your device anywhere in the world - no cellular or GPS required.

![ESP32 Tracker](https://img.shields.io/badge/ESP32-Supported-green) ![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue) ![License](https://img.shields.io/badge/License-MIT-yellow)

## How It Works

```
┌─────────────┐    BLE Beacon    ┌─────────────┐    Encrypted    ┌─────────────┐
│   ESP32     │ ───────────────> │   iPhones   │ ─────────────> │   Apple     │
│  (Your Tag) │                  │  (Nearby)   │    Upload      │  Servers    │
└─────────────┘                  └─────────────┘                └──────┬──────┘
                                                                       │
┌─────────────┐    Decrypted     ┌─────────────┐    Download    ┌──────┴──────┐
│   You See   │ <─────────────── │   Your Mac  │ <───────────── │   Encrypted │
│  Location   │                  │  (FindMy.py)│                │   Reports   │
└─────────────┘                  └─────────────┘                └─────────────┘
```

1. **ESP32 broadcasts** a Bluetooth beacon with your public key
2. **Nearby iPhones** detect it, encrypt their GPS location with your public key, and upload to Apple
3. **You download** the encrypted reports and decrypt with your private key
4. **See location** on the web dashboard or CLI

## Features

- **Free global tracking** - Uses Apple's billion-device Find My network
- **No subscription** - Unlike commercial trackers
- **Privacy-focused** - Only you can decrypt your device's location
- **Web dashboard** - Interactive map to view your tracker's location
- **CLI tool** - Quick location fetch from terminal
- **Low power** - ESP32 can run for months on battery

## Requirements

### Hardware
- ESP32 development board (ESP32-WROOM, ESP32-WROVER, etc.)
- USB cable for programming
- (Optional) Battery for portable use

### Software
- macOS, Linux, or Windows with WSL
- Python 3.12+
- ESP-IDF v5.x (for building firmware)
- Apple ID with 2FA enabled

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/divyarthjain/esp32-airtag-tracker.git
cd esp32-airtag-tracker
```

### 2. Install Python Dependencies

```bash
pip install FindMy cryptography
```

### 3. Generate Your Keys

```bash
cd scripts
python3 generate_keys.py
```

This outputs:
- `private_key.pem` - Keep this safe! Needed to decrypt locations
- C array to copy into the firmware

### 4. Flash the ESP32

```bash
# Install ESP-IDF first (see docs/ESP_IDF_SETUP.md)
cd firmware
# Copy the C array from step 3 into main/openhaystack_main.c
idf.py build
./flash_esp32.sh -p /dev/cu.usbserial-XXX
```

### 5. Fetch Your Location

```bash
cd scripts
python3 fetch_location.py
```

First run will prompt for Apple ID login. Your session is saved for future use.

### 6. Open the Dashboard

```bash
python3 web_dashboard.py
```

Opens an interactive map at http://localhost:8080

---

## 🤖 AI Agent Setup Assistant

If you are using an AI coding assistant (like Claude Code, GitHub Copilot, or ChatGPT), copy and paste this prompt to have it automate the setup for you:

> "I want you to help me set up the ESP32 AirTag Tracker project from `https://github.com/divyarthjain/esp32-airtag-tracker.git`. 
> 1. Install Python dependencies: `pip install FindMy cryptography`.
> 2. Generate new keys using `scripts/generate_keys.py`.
> 3. Guide me through installing ESP-IDF v5.2.2 as described in `docs/ESP_IDF_SETUP.md`.
> 4. Help me copy the generated public key array into `firmware/main/openhaystack_main.c`.
> 5. Build the firmware using `idf.py build` in the `firmware/` directory.
> 6. Finally, explain how to flash the device and run the web dashboard."

## Project Structure

```
esp32-airtag-tracker/
├── firmware/                 # ESP32 firmware (ESP-IDF project)
│   ├── main/
│   │   └── openhaystack_main.c   # Main BLE advertising code
│   ├── CMakeLists.txt
│   ├── sdkconfig
│   ├── partitions.csv
│   └── flash_esp32.sh       # Flashing script
├── scripts/                  # Python tools
│   ├── generate_keys.py     # Generate Find My keypair
│   ├── fetch_location.py    # CLI location fetcher
│   └── web_dashboard.py     # Web UI with map
├── docs/                     # Documentation
│   ├── ESP_IDF_SETUP.md     # ESP-IDF installation guide
│   ├── TROUBLESHOOTING.md   # Common issues and fixes
│   └── HOW_IT_WORKS.md      # Technical deep-dive
└── README.md
```

## Documentation

| Document | Description |
|----------|-------------|
| [ESP-IDF Setup](docs/ESP_IDF_SETUP.md) | How to install ESP-IDF build tools |
| [Troubleshooting](docs/TROUBLESHOOTING.md) | Common problems and solutions |
| [How It Works](docs/HOW_IT_WORKS.md) | Technical explanation of Find My protocol |

## FAQ

### How long until I see a location?
15-30 minutes after deploying. iPhones need to detect your ESP32 and upload reports.

### What's the battery life?
With a 1000mAh battery, expect 2-6 months depending on broadcast interval settings.

### Can I track multiple ESP32s?
Yes! Generate a new keypair for each device and add them to the scripts.

### Does this work outside the US?
Yes, anywhere iPhones exist. The Find My network is global.

### Is this legal?
For personal use tracking your own items, yes. Don't use for tracking people without consent.

## Acknowledgments

- [OpenHaystack](https://github.com/seemoo-lab/openhaystack) - Original research and firmware
- [FindMy.py](https://github.com/malmeloo/FindMy.py) - Python library for Find My network
- Apple's Find My Network - The infrastructure that makes this possible

## License

MIT License - See [LICENSE](LICENSE) for details.

## Disclaimer

This project is for educational purposes. Use responsibly and ethically. Not affiliated with Apple Inc.
