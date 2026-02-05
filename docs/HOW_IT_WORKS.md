# How It Works: Technical Deep Dive

This document explains the technical details of how the ESP32 AirTag Tracker works with Apple's Find My network.

## Overview

Apple's Find My network uses a clever combination of:
- Bluetooth Low Energy (BLE) advertising
- Elliptic Curve Cryptography (P-224)
- Crowdsourced location from billions of Apple devices

## The Protocol

### 1. Key Generation

We generate a P-224 elliptic curve keypair:

```
Private Key: 28 bytes (kept secret)
Public Key: 28 bytes (X-coordinate only, broadcast by ESP32)
```

The public key is called the "advertisement key" because it's broadcast via BLE.

### 2. BLE Advertising (ESP32)

The ESP32 broadcasts a specially formatted BLE advertisement:

```
┌────────────────────────────────────────────────────────────┐
│ BLE Advertisement Payload                                   │
├────────────────────────────────────────────────────────────┤
│ Company ID: 0x004C (Apple)                                 │
│ Type: 0x12 (Offline Finding)                               │
│ Length: 25 bytes                                           │
│ Status: 1 byte                                             │
│ Public Key: 22 bytes (partial)                             │
│ Key Bits: 1 byte (remaining bits)                          │
│ Hint: 1 byte                                               │
└────────────────────────────────────────────────────────────┘
```

The public key is split across the advertisement and the BLE MAC address.

### 3. Detection by iPhones

When an iPhone with Find My enabled detects this advertisement:

1. It captures its current GPS location
2. Derives an ephemeral key using ECDH
3. Encrypts the location with AES-GCM
4. Uploads the encrypted report to Apple's servers

```
iPhone Process:
1. Receive BLE advertisement with public_key
2. Generate ephemeral_private, ephemeral_public
3. shared_secret = ECDH(ephemeral_private, public_key)
4. encryption_key = KDF(shared_secret)
5. encrypted_location = AES-GCM(encryption_key, gps_coordinates)
6. Upload: (SHA256(public_key), ephemeral_public, encrypted_location)
```

### 4. Apple's Servers

Apple stores reports indexed by `SHA256(public_key)`. They cannot:
- Decrypt the location (they don't have the private key)
- Know who owns the device
- Link reports to Apple IDs

### 5. Fetching Reports

We authenticate with Apple using:
- Apple ID credentials
- Anisette headers (device identity simulation)
- Search Party Token (iCloud authentication)

Request:
```json
POST https://gateway.icloud.com/acsnservice/fetch
{
  "ids": ["base64(SHA256(public_key))"],
  "startDate": 1234567890000,
  "endDate": 1234567890000
}
```

### 6. Decrypting Reports

For each report received:

```python
# Report contains:
# - ephemeral_public: The iPhone's ephemeral public key
# - encrypted_data: AES-GCM encrypted location
# - tag: Authentication tag

# Decryption:
shared_secret = ECDH(our_private_key, ephemeral_public)
derived_key = KDF(shared_secret)
decryption_key = derived_key[0:16]
iv = derived_key[16:32]
location = AES-GCM-Decrypt(decryption_key, iv, encrypted_data, tag)
```

The decrypted location contains:
- Latitude (4 bytes, big-endian int32 / 10^7)
- Longitude (4 bytes, big-endian int32 / 10^7)
- Accuracy (1 byte, meters)
- Status (1 byte)
- Timestamp (4 bytes, Unix seconds)

## Security Properties

### Privacy
- Only the private key holder can decrypt locations
- Apple cannot read locations
- Reports are anonymous (no link to Apple ID)

### Integrity
- AES-GCM provides authentication
- Tampered reports fail decryption

### Limitations
- Anyone with the public key can track the device
- No revocation mechanism (key must be changed physically)
- Relies on iPhone density for coverage

## References

1. [Who Can Find My Devices?](https://www.petsymposium.org/2021/files/papers/issue3/popets-2021-0045.pdf) - Original research paper
2. [Apple Find My Accessory Specification](https://developer.apple.com/find-my/) - Official documentation
3. [OpenHaystack](https://github.com/seemoo-lab/openhaystack) - Reference implementation
