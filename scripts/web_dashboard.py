#!/usr/bin/env python3
"""
ESP32 AirTag Web Dashboard

Local web server with interactive map UI for tracking your ESP32.
Opens automatically in browser at http://localhost:8080
"""

import argparse
import json
import logging
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from findmy import KeyPair
from findmy import AppleAccount, LocalAnisetteProvider

SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_KEY_FILE = SCRIPT_DIR / "private_key.pem"
STORE_PATH = SCRIPT_DIR / "apple_account.json"
ANISETTE_LIBS_PATH = SCRIPT_DIR / "anisette_libs.bin"
PORT = 8080

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

account = None
key = None
last_location = None


def load_private_key(key_file: Path) -> bytes:
    pem_data = key_file.read_text()
    private_key = serialization.load_pem_private_key(
        pem_data.encode(), password=None, backend=default_backend()
    )
    return private_key.private_numbers().private_value.to_bytes(28, "big")


def init_account(key_file: Path):
    global account, key

    if not key_file.exists():
        logger.error(f"Key file not found: {key_file}")
        return False

    raw_key = load_private_key(key_file)
    key = KeyPair(raw_key)
    logger.info(f"Loaded key: {key.adv_key_b64}")

    try:
        account = AppleAccount.from_json(
            str(STORE_PATH), anisette_libs_path=str(ANISETTE_LIBS_PATH)
        )
        logger.info(f"Loaded account: {account.account_name}")
        return True
    except FileNotFoundError:
        logger.error("No saved session. Run fetch_location.py first!")
        return False


def fetch_location():
    global last_location, account

    if not account or not key:
        return None

    try:
        location = account.fetch_location(key)
        if location:
            last_location = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "timestamp": str(location.timestamp),
                "fetched_at": datetime.now().isoformat(),
            }
            account.to_json(str(STORE_PATH))
        return last_location
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return None


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ESP32 AirTag Tracker</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        #header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 20px; text-align: center;
        }
        #header h1 { font-size: 24px; margin-bottom: 5px; }
        #map { height: calc(100vh - 180px); width: 100%; }
        #controls {
            padding: 15px 20px; background: #f8f9fa; border-top: 1px solid #e9ecef;
            display: flex; justify-content: space-between; align-items: center;
        }
        #status { font-size: 14px; color: #666; }
        #status.loading { color: #007bff; }
        #status.success { color: #28a745; }
        #status.error { color: #dc3545; }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; border: none; padding: 12px 24px; border-radius: 8px;
            cursor: pointer; font-size: 14px; font-weight: 600;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        #info { background: white; padding: 15px 20px; font-size: 13px; }
        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        .info-label { font-size: 11px; text-transform: uppercase; color: #999; }
        .info-value { font-weight: 600; color: #333; }
    </style>
</head>
<body>
    <div id="header">
        <h1>ESP32 AirTag Tracker</h1>
        <p>Powered by Apple Find My Network</p>
    </div>
    <div id="map"></div>
    <div id="controls">
        <div id="status">Ready</div>
        <button onclick="refreshLocation()" id="refreshBtn">Refresh Location</button>
    </div>
    <div id="info">
        <div class="info-grid">
            <div><div class="info-label">Latitude</div><div class="info-value" id="lat">--</div></div>
            <div><div class="info-label">Longitude</div><div class="info-value" id="lng">--</div></div>
            <div><div class="info-label">Last Seen</div><div class="info-value" id="timestamp">--</div></div>
        </div>
    </div>
    <script>
        const map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap'
        }).addTo(map);
        let marker = null;

        async function refreshLocation() {
            const btn = document.getElementById('refreshBtn');
            const status = document.getElementById('status');
            btn.disabled = true;
            status.textContent = 'Fetching...';
            status.className = 'loading';

            try {
                const r = await fetch('/api/location');
                const data = await r.json();
                if (data.latitude) {
                    if (marker) marker.setLatLng([data.latitude, data.longitude]);
                    else marker = L.marker([data.latitude, data.longitude]).addTo(map);
                    map.setView([data.latitude, data.longitude], 15);
                    document.getElementById('lat').textContent = data.latitude.toFixed(6);
                    document.getElementById('lng').textContent = data.longitude.toFixed(6);
                    document.getElementById('timestamp').textContent = data.timestamp || '--';
                    status.textContent = 'Updated!';
                    status.className = 'success';
                } else {
                    status.textContent = 'No location found';
                    status.className = 'error';
                }
            } catch (e) {
                status.textContent = 'Error: ' + e.message;
                status.className = 'error';
            }
            btn.disabled = false;
        }
        refreshLocation();
    </script>
</body>
</html>"""


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path == "/api/location":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            loc = fetch_location()
            self.wfile.write(json.dumps(loc or {"error": "No location"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    parser = argparse.ArgumentParser(description="ESP32 tracker web dashboard")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    print("=" * 60)
    print("ESP32 AirTag Web Dashboard")
    print("=" * 60 + "\n")

    if not init_account(args.key_file):
        print("\nRun 'python3 fetch_location.py' first to log in!")
        return 1

    print(f"\nStarting server at http://localhost:{args.port}")
    print("Press Ctrl+C to stop\n")

    try:
        import webbrowser

        webbrowser.open(f"http://localhost:{args.port}")
    except:
        pass

    server = HTTPServer(("localhost", args.port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
    return 0


if __name__ == "__main__":
    exit(main())
