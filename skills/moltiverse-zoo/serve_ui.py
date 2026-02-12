#!/usr/bin/env python3
"""
Serve a lightweight UI for Moltiverse Zoo with wallet authentication.
"""
import argparse
import json
import os
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from ecosystem_status import get_ecosystem_status
from spawn_agent import spawn_agent
from wallet_auth import (
    create_auth_challenge,
    verify_auth_signature,
    get_session_token,
    verify_session_token
)

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent.parent / ".env")

BASE_DIR = Path(__file__).parent
UI_DIR = BASE_DIR / "ui"
SIM_PROCESS: subprocess.Popen | None = None

# Require token balance for control endpoints (set to 0 to disable)
MIN_TOKEN_BALANCE = float(os.getenv("MIN_TOKEN_BALANCE", "0"))

# Reown AppKit configuration
REOWN_PROJECT_ID = os.getenv("REOWN_PROJECT_ID", "")
MONAD_RPC_URL = os.getenv("MONAD_RPC_URL", "https://rpc.monad.xyz")
MONAD_CHAIN_ID = int(os.getenv("MONAD_CHAIN_ID", "143"))


def _check_auth(request_handler) -> tuple[bool, str | None]:
    """
    Check if request has valid auth token or no auth required.
    Returns (is_authenticated, wallet_address or error_message)
    """
    # If token balance not required, skip auth
    if MIN_TOKEN_BALANCE == 0:
        return True, None
    
    # Check Authorization header
    auth_header = request_handler.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False, "Missing or invalid Authorization header"
    
    token = auth_header[7:]
    wallet = verify_session_token(token)
    if not wallet:
        return False, "Invalid or expired session token"
    
    return True, wallet


def _send_json(request_handler, status: int, data: dict):
    """Helper to send JSON response."""
    payload = json.dumps(data).encode("utf-8")
    request_handler.send_response(status)
    request_handler.send_header("Content-Type", "application/json")
    request_handler.send_header("Content-Length", str(len(payload)))
    request_handler.end_headers()
    request_handler.wfile.write(payload)

# Require token balance for control endpoints (set to 0 to disable)
MIN_TOKEN_BALANCE = float(os.getenv("MIN_TOKEN_BALANCE", "0"))


class ZooHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        
        if parsed.path == "/api/auth/challenge":
            # Create authentication challenge
            wallet = self.headers.get("X-Wallet-Address")
            if not wallet:
                return _send_json(self, 400, {"error": "Missing X-Wallet-Address header"})
            
            try:
                challenge = create_auth_challenge(wallet)
                return _send_json(self, 200, {
                    "status": "ok",
                    "challenge": challenge,
                    "note": "Sign this message with your wallet and send back to /api/auth/verify"
                })
            except Exception as e:
                return _send_json(self, 400, {"error": str(e)})
        
        if parsed.path == "/api/status":
            data = get_ecosystem_status()
            payload = json.dumps(data).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if parsed.path == "/api/config":
            payload = json.dumps({
                "minTokenBalance": MIN_TOKEN_BALANCE,
                "reownProjectId": REOWN_PROJECT_ID,
                "monadRpcUrl": MONAD_RPC_URL,
                "monadChainId": MONAD_CHAIN_ID,
            }).encode("utf-8")
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

        # Auth endpoints (no wallet required)
        if parsed.path == "/api/auth/verify":
            wallet = payload.get("wallet")
            signature = payload.get("signature")
            if not wallet or not signature:
                return _send_json(self, 400, {"error": "Missing wallet or signature"})
            
            result = verify_auth_signature(wallet, signature, int(MIN_TOKEN_BALANCE))

            if result.get("authenticated"):
                # Generate session token without re-running verification (verify_auth_signature already ran)
                session_token = get_session_token(wallet)
                return _send_json(self, 200, {
                    "status": "ok",
                    "session_token": session_token,
                    "wallet": wallet,
                    "token_balance": result.get("token_balance"),
                    "message": "Authenticated! Use session_token in Authorization header"
                })
            else:
                return _send_json(self, 401, {
                    "error": result.get("error", "Authentication failed"),
                    "token_balance": result.get("token_balance")
                })

        # Protected endpoints (require auth)
        if parsed.path.startswith("/api/control/"):
            is_auth, auth_info = _check_auth(self)
            if not is_auth:
                return _send_json(self, 401, {"error": auth_info})

        # Control endpoints
        if parsed.path == "/api/control/spawn":
            agent_type = payload.get("type", "trader")
            energy = int(payload.get("energy", 100))
            agent = spawn_agent(agent_type, energy)
            return _send_json(self, 200, {"status": "ok", "agent": agent})

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
            return _send_json(self, 200, {"status": "ok"})

        if parsed.path == "/api/control/sim/stop":
            if SIM_PROCESS is not None and SIM_PROCESS.poll() is None:
                SIM_PROCESS.terminate()
                SIM_PROCESS = None
            return _send_json(self, 200, {"status": "ok"})

        if parsed.path == "/api/control/join":
            agent_type = payload.get("type", "trader")
            energy = int(payload.get("energy", 100))
            agent_name = payload.get("name", "")
            try:
                agent = spawn_agent(agent_type, energy, name=agent_name)
                return _send_json(self, 200, {
                    "status": "ok",
                    "agent": agent,
                    "message": f"Agent {agent.get('id')} joined the Moltiverse Zoo!"
                })
            except Exception as e:
                return _send_json(self, 500, {"status": "error", "error": str(e)})

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
