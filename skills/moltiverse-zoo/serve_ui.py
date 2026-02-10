#!/usr/bin/env python3
"""
Serve a lightweight UI for Moltiverse Zoo.
"""
import argparse
import json
import os
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ecosystem_status import get_ecosystem_status
from spawn_agent import spawn_agent

BASE_DIR = Path(__file__).parent
UI_DIR = BASE_DIR / "ui"
SIM_PROCESS: subprocess.Popen | None = None


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

        if parsed.path == "/api/control/status":
            running = SIM_PROCESS is not None and SIM_PROCESS.poll() is None
            payload = json.dumps({"running": running}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed.path == "/":
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        global SIM_PROCESS
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {}

        if parsed.path == "/api/control/spawn":
            agent_type = payload.get("type", "trader")
            energy = int(payload.get("energy", 100))
            agent = spawn_agent(agent_type, energy)
            response = json.dumps({"status": "ok", "agent": agent}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return

        if parsed.path == "/api/control/sim/start":
            if SIM_PROCESS is None or SIM_PROCESS.poll() is not None:
                steps = str(payload.get("steps", 50))
                interval = str(payload.get("interval", 1.5))
                provider = payload.get("provider", "ollama")
                model = payload.get("model")
                cmd = [
                    sys.executable,
                    str(BASE_DIR / "run_simulation.py"),
                    "--steps",
                    steps,
                    "--interval",
                    interval,
                    "--provider",
                    provider,
                ]
                if model:
                    cmd.extend(["--model", model])
                SIM_PROCESS = subprocess.Popen(cmd)
            response = json.dumps({"status": "ok"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return

        if parsed.path == "/api/control/sim/stop":
            if SIM_PROCESS is not None and SIM_PROCESS.poll() is None:
                SIM_PROCESS.terminate()
                SIM_PROCESS = None
            response = json.dumps({"status": "ok"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            return

        self.send_response(404)
        self.end_headers()


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
