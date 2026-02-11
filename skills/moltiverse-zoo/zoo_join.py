#!/usr/bin/env python3
"""
Join the Moltiverse Zoo from a remote OpenClaw agent.

Usage:
  python3 zoo_join.py --gateway-url http://localhost:8787 --type trader --energy 100 [--name "My Agent"]
  
Or set ZOO_GATEWAY_URL environment variable:
  export ZOO_GATEWAY_URL=http://localhost:8787
  python3 zoo_join.py --type breeder --energy 120
"""
import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError


def join_zoo(gateway_url: str, agent_type: str = "trader", energy: int = 100, name: str = "") -> dict:
    """
    Join the Moltiverse Zoo by calling the /api/control/join endpoint.
    
    Args:
        gateway_url: Base URL of the zoo UI server (e.g., http://localhost:8787)
        agent_type: Type of agent: trader, breeder, or explorer
        energy: Initial energy (default 100)
        name: Optional name for the agent
    
    Returns:
        Response dict with agent details or error
    """
    url = f"{gateway_url}/api/control/join"
    payload = {
        "type": agent_type,
        "energy": energy,
        "name": name
    }
    
    try:
        req = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except URLError as e:
        return {"status": "error", "error": f"Connection failed: {e.reason}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid response: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(
        description="Join the Moltiverse Zoo as a new agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 zoo_join.py --gateway-url http://localhost:8787 --type trader
  python3 zoo_join.py --gateway-url https://my-zoo.example.com --type breeder --energy 150 --name "Alice"
  
Set ZOO_GATEWAY_URL env var to avoid --gateway-url flag:
  export ZOO_GATEWAY_URL=http://localhost:8787
  python3 zoo_join.py --type explorer --energy 120
        """
    )
    
    gateway_url = os.getenv("ZOO_GATEWAY_URL", "http://localhost:8787")
    
    parser.add_argument("--gateway-url", default=gateway_url, help="Zoo UI server URL (default: $ZOO_GATEWAY_URL or http://localhost:8787)")
    parser.add_argument("--type", dest="agent_type", default="trader", choices=["trader", "breeder", "explorer"], help="Agent type (default: trader)")
    parser.add_argument("--energy", type=int, default=100, help="Initial energy (default: 100)")
    parser.add_argument("--name", default="", help="Optional agent name")
    
    args = parser.parse_args()
    
    print(f"🦞 Joining Moltiverse Zoo at {args.gateway_url}...")
    print(f"   Type: {args.agent_type} | Energy: {args.energy}" + (f" | Name: {args.name}" if args.name else ""))
    
    result = join_zoo(args.gateway_url, args.agent_type, args.energy, args.name)
    
    if result.get("status") == "ok":
        agent = result.get("agent", {})
        print(f"\n✅ Success! {result.get('message', 'Agent joined.')}")
        print(f"   Agent ID: {agent.get('id')}")
        print(f"   Type: {agent.get('type')}")
        print(f"   Energy: {agent.get('energy')}")
        print(f"   Generation: {agent.get('generation')}")
        return 0
    else:
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
