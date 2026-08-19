"""
SwingPulse Mobile Portal Server
Serves the mobile web dashboard and handles live scan API requests.
Allows accessing from any smartphone / browser on the same Wi-Fi network.
"""

import os
import sys
import json
import socket
import http.server
import socketserver
from pathlib import Path

# Ensure UTF-8 output on Windows streams
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DEFAULT_PORTS = [int(os.environ.get("PORT", 8080)), 8085, 8088, 8000, 8090]
WEB_DIR = Path(__file__).parent / "web"
DATA_FILE = WEB_DIR / "data" / "latest.json"

def get_local_ip():
    """Detect the local LAN IP address for mobile access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

class PortalRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        if self.path == "/api/recommendations":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if DATA_FILE.exists():
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.wfile.write(f.read().encode("utf-8"))
            else:
                self.wfile.write(b'{"recommendations":[]}')
            return
        
        # Default static file handler
        super().do_GET()

def start_server():
    local_ip = get_local_ip()
    socketserver.TCPServer.allow_reuse_address = True

    httpd = None
    active_port = None

    for port in DEFAULT_PORTS:
        try:
            httpd = socketserver.TCPServer(("", port), PortalRequestHandler)
            active_port = port
            break
        except (OSError, PermissionError):
            continue

    if not httpd:
        print("[ERROR] Could not bind to any available port.")
        sys.exit(1)

    mobile_url = f"http://{local_ip}:{active_port}"
    desktop_url = f"http://localhost:{active_port}"

    print("=" * 65)
    print(" 🚀 SWINGPULSE MOBILE PORTAL IS RUNNING!")
    print("=" * 65)
    print(f"\n 📱 TO VIEW ON YOUR MOBILE PHONE (Connected to same Wi-Fi):")
    print(f"    👉  {mobile_url}")
    print(f"\n 💻 TO VIEW ON THIS PC:")
    print(f"    👉  {desktop_url}")
    print("\n" + "=" * 65)
    print(" [TIP] On iPhone (Safari) or Android (Chrome), tap 'Add to Home Screen'")
    print("       to use it as a full-screen mobile trading app!")
    print("=" * 65 + "\n")

    with httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down portal server...")

if __name__ == "__main__":
    start_server()

