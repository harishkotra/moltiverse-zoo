#!/usr/bin/env python3
"""
Serve a lightweight UI for Moltiverse Zoo.
"""
import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ecosystem_status import get_ecosystem_status

BASE_DIR = Path(__file__).parent
UI_DIR = BASE_DIR / "ui"


class ZooHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            data = get_ecosystem_status()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed.path == "/":
            self.path = "/index.html"

        return super().do_GET()


def main():
    parser = argparse.ArgumentParser(description="Serve Moltiverse Zoo UI")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()

    os.chdir(UI_DIR)
    server = HTTPServer(("127.0.0.1", args.port), ZooHandler)
    print(f"Moltiverse Zoo UI running at http://127.0.0.1:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
