# Troubleshooting Guide

Common issues and solutions for the ESP32 AirTag Tracker.

## Location Not Found

### Symptoms
- `fetch_location.py` returns "No location found"
- Dashboard shows empty map

### Solutions

1. **Wait longer** - First detection takes 15-30 minutes
   - iPhones need to detect your ESP32 and upload reports
   - Reports propagate through Apple's servers

2. **Move to a populated area**
   - More iPhones nearby = faster detection
   - Works best in cities, malls, busy streets

3. **Verify ESP32 is broadcasting**
   ```bash
   # Use a BLE scanner app on your phone
   # Look for device with MAC starting with your public key bytes
   ```

4. **Check ESP32 power**
   - LED should blink periodically
   - Try a different USB port/cable

5. **Verify firmware has correct key**
   ```bash
   # Re-flash with your public key
   cd firmware
   get_idf
   idf.py build flash
   ```

## Login Issues

### "Invalid credentials" error

1. **Check Apple ID/password** - Must be exact
2. **2FA is required** - Enable it in Apple ID settings
3. **Use SMS 2FA** - Trusted device sometimes has issues
4. **App-specific password not needed** - Use your regular password

### "Session expired" error

```bash
# Delete saved session and re-login
rm scripts/apple_account.json
python3 scripts/fetch_location.py
```

### "Too many requests" error

- Wait 15-30 minutes before retrying
- Apple rate-limits the API

## Build Errors

### "ESP-IDF not found"

```bash
# Activate ESP-IDF environment first
get_idf
# Then run build commands
```

### "Component not found"

```bash
cd firmware
idf.py fullclean
idf.py build
```

### Compiler errors in openhaystack_main.c

- Ensure public key array is exactly 28 bytes
- Check for typos in the hex values
- Format: `{0xXX, 0xXX, ...}` with 28 values

## Flash Errors

### "Failed to connect"

1. **Hold BOOT button** while running flash command
2. **Try different USB cable** - Must be data cable
3. **Check port**:
   ```bash
   # macOS
   ls /dev/cu.usb*
   
   # Linux
   ls /dev/ttyUSB*
   ```

### "Permission denied" (Linux)

```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Wrong chip detected

```bash
# Specify chip explicitly
idf.py set-target esp32
idf.py build
```

## Web Dashboard Issues

### "No saved session" error

Run `fetch_location.py` first to log in:
```bash
cd scripts
python3 fetch_location.py
# Complete login
python3 web_dashboard.py
```

### Port already in use

```bash
# Kill existing process
lsof -i :8080 | grep Python | awk '{print $2}' | xargs kill

# Or use different port
python3 web_dashboard.py --port 8081
```

### Map not loading

- Check internet connection (map tiles load from OpenStreetMap)
- Try a different browser
- Clear browser cache

## Key Generation Issues

### "Module not found: cryptography"

```bash
pip install cryptography
# or
pip3 install cryptography
```

### Generated key doesn't work

- Ensure you copied the FULL C array (28 bytes)
- Don't add extra spaces or modify the format
- Rebuild firmware after changing the key

## Still Having Issues?

1. Check the [GitHub Issues](https://github.com/divyarthjain/esp32-airtag-tracker/issues)
2. Open a new issue with:
   - Your OS and Python version
   - Full error message
   - Steps to reproduce
