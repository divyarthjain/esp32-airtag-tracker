#!/usr/bin/env python3
"""
ESP32 AirTag Location Fetcher

Retrieves location reports from Apple's Find My network for your custom ESP32 tracker.

Usage:
    python3 fetch_location.py [--key-file PATH]

First run will prompt for Apple ID login. Session is saved for future use.
"""

import argparse
import logging
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from findmy import KeyPair
from findmy import (
    AppleAccount,
    LocalAnisetteProvider,
    RemoteAnisetteProvider,
    LoginState,
    SmsSecondFactorMethod,
    TrustedDeviceSecondFactorMethod,
)

SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_KEY_FILE = SCRIPT_DIR / "private_key.pem"
STORE_PATH = SCRIPT_DIR / "apple_account.json"
ANISETTE_LIBS_PATH = SCRIPT_DIR / "anisette_libs.bin"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def load_private_key(key_file: Path) -> bytes:
    """Load and extract raw 28-byte private key from PEM file."""
    if not key_file.exists():
        raise FileNotFoundError(
            f"Private key file not found: {key_file}\nRun generate_keys.py first!"
        )

    pem_data = key_file.read_text()
    private_key = serialization.load_pem_private_key(
        pem_data.encode(), password=None, backend=default_backend()
    )
    return private_key.private_numbers().private_value.to_bytes(28, "big")


def login(account: AppleAccount) -> None:
    """Interactive login with 2FA support."""
    email = input("Apple ID email: ")
    password = input("Apple ID password: ")

    state = account.login(email, password)

    if state == LoginState.REQUIRE_2FA:
        print("\n2FA Required. Available methods:")
        methods = account.get_2fa_methods()

        for i, method in enumerate(methods):
            if isinstance(method, TrustedDeviceSecondFactorMethod):
                print(f"  {i} - Trusted Device")
            elif isinstance(method, SmsSecondFactorMethod):
                print(f"  {i} - SMS to {method.phone_number}")

        idx = int(input("\nSelect method: "))
        method = methods[idx]

        if isinstance(method, SmsSecondFactorMethod):
            method.request()
            print("SMS sent!")

        code = input("Enter 2FA code: ")
        method.submit(code)
        print("Login successful!")


def get_account() -> AppleAccount:
    """Load saved session or perform interactive login."""
    try:
        logger.info(f"Loading session from {STORE_PATH}...")
        return AppleAccount.from_json(
            str(STORE_PATH), anisette_libs_path=str(ANISETTE_LIBS_PATH)
        )
    except FileNotFoundError:
        logger.info("No saved session. Starting login...")
        ani = LocalAnisetteProvider(libs_path=str(ANISETTE_LIBS_PATH))
        acc = AppleAccount(ani)
        login(acc)
        acc.to_json(str(STORE_PATH))
        return acc


def main():
    parser = argparse.ArgumentParser(
        description="Fetch ESP32 location from Find My network"
    )
    parser.add_argument(
        "--key-file",
        type=Path,
        default=DEFAULT_KEY_FILE,
        help="Path to private key PEM file",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("ESP32 AirTag Location Fetcher")
    print("=" * 60 + "\n")

    try:
        raw_key = load_private_key(args.key_file)
        key = KeyPair(raw_key)
        logger.info(f"Loaded key: {key.adv_key_b64}")
    except Exception as e:
        logger.error(f"Failed to load key: {e}")
        return 1

    try:
        acc = get_account()
        print(f"\nLogged in as: {acc.account_name}")
    except Exception as e:
        logger.error(f"Login failed: {e}")
        return 1

    print("\nFetching location from Apple...")
    try:
        location = acc.fetch_location(key)
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        acc.to_json(str(STORE_PATH))
        return 1

    print("\n" + "=" * 60)
    if location is None:
        print("NO LOCATION FOUND")
        print("\nPossible reasons:")
        print("  - ESP32 hasn't been detected by any iPhone yet")
        print("  - Wait 15-30 minutes after first deployment")
        print("  - Move to a populated area with iPhones nearby")
    else:
        print("LOCATION FOUND!")
        print("=" * 60)
        print(f"  Latitude:  {location.latitude}")
        print(f"  Longitude: {location.longitude}")
        print(f"  Timestamp: {location.timestamp}")
        print(
            f"\nGoogle Maps: https://www.google.com/maps?q={location.latitude},{location.longitude}"
        )

        report_path = SCRIPT_DIR / "last_location.json"
        location.to_json(str(report_path))
        print(f"\nSaved to: {report_path}")

    acc.to_json(str(STORE_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
