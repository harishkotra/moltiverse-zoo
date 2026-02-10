#!/usr/bin/env python3
"""
Get current ecosystem status - all active agents, resources, transactions.
"""
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

def get_ecosystem_status() -> dict:
    """Load and return current ecosystem state."""
    agents_file = DATA_DIR / "agents.json"
    resources_file = DATA_DIR / "resources.json"
    transactions_file = DATA_DIR / "transactions.json"
    
    # Create data dir if it doesn't exist
    DATA_DIR.mkdir(exist_ok=True)
    
    # Load or initialize data files
    agents = []
    if agents_file.exists():
        with open(agents_file) as f:
            agents = json.load(f)
    
    resources = {"global_pool": {"food": 1000, "materials": 500}}
    if resources_file.exists():
        with open(resources_file) as f:
            resources = json.load(f)
    
    transactions = []
    if transactions_file.exists():
        with open(transactions_file) as f:
            transactions = json.load(f)
    
    # Calculate statistics
    total_energy = sum(a.get("energy", 0) for a in agents)
    active_agents = [a for a in agents if a.get("energy", 0) > 0]
    dead_agents = [a for a in agents if a.get("energy", 0) <= 0]
    
    agent_types = {}
    for agent in active_agents:
        agent_type = agent.get("type", "unknown")
        agent_types[agent_type] = agent_types.get(agent_type, 0) + 1
    
    return {
        "status": "running",
        "statistics": {
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "dead_agents": len(dead_agents),
            "total_energy": total_energy,
            "agent_types": agent_types,
            "total_transactions": len(transactions)
        },
        "resources": resources,
        "agents": active_agents[:10],  # Top 10 active agents
        "recent_transactions": transactions[-5:]  # Last 5 transactions
    }

def main():
    status = get_ecosystem_status()
    print(json.dumps(status, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
