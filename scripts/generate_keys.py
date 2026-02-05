#!/usr/bin/env python3
"""
ESP32 AirTag Key Generator

Generates P-224 elliptic curve keypairs compatible with Apple's Find My network.
Outputs the public key in formats needed for the ESP32 firmware.
"""

import argparse
import base64
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def generate_keypair():
    """Generate a new P-224 keypair for Find My network."""
    private_key = ec.generate_private_key(ec.SECP224R1(), default_backend())
    return private_key


def format_c_array(data: bytes, name: str = "public_key") -> str:
    """Format bytes as C array for ESP32 firmware."""
    hex_bytes = ", ".join(f"0x{b:02x}" for b in data)
    return f"static uint8_t {name}[] = {{{hex_bytes}}};"


def main():
    parser = argparse.ArgumentParser(description="Generate Find My keypair for ESP32")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("private_key.pem"),
        help="Output path for private key PEM file",
    )
    parser.add_argument(
        "--name", default="ESP32 Tracker", help="Name for the accessory"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("ESP32 AirTag Key Generator")
    print("=" * 70 + "\n")

    private_key = generate_keypair()

    private_numbers = private_key.private_numbers()
    public_numbers = private_key.public_key().public_numbers()

    private_bytes = private_numbers.private_value.to_bytes(28, "big")
    public_x = public_numbers.x.to_bytes(28, "big")

    pem_data = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    args.output.write_bytes(pem_data)

    print(f"Generated new P-224 keypair\n")
    print("-" * 70)
    print("ADVERTISEMENT KEY (Base64) - For reference:")
    print("-" * 70)
    print(base64.b64encode(public_x).decode())
    print()

    print("-" * 70)
    print("C ARRAY - Copy to firmware/main/openhaystack_main.c:")
    print("-" * 70)
    print("static uint8_t public_keys[][28] = {")
    hex_line = "    {" + ", ".join(f"0x{b:02x}" for b in public_x) + "},"
    print(hex_line)
    print("};")
    print()

    print("-" * 70)
    print(f"PRIVATE KEY - Saved to: {args.output}")
    print("-" * 70)
    print("Keep this file safe! You need it to decrypt location reports.")
    print()

    print("=" * 70)
    print("NEXT STEPS:")
    print("=" * 70)
    print("1. Copy the C array above into firmware/main/openhaystack_main.c")
    print("2. Build firmware: cd firmware && idf.py build")
    print("3. Flash ESP32: ./flash_esp32.sh -p /dev/YOUR_PORT")
    print("4. Fetch location: python3 fetch_location.py")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
