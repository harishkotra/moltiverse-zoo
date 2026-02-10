#!/usr/bin/env python3
"""
Spawn a new agent in the Moltiverse Zoo ecosystem.
Uses OpenClaw's sessions_spawn tool via the gateway.
"""
import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Literal

AgentType = Literal["trader", "breeder", "explorer"]

DATA_DIR = Path(__file__).parent / "data"
AGENTS_FILE = DATA_DIR / "agents.json"

AGENT_PROMPTS = {
    "trader": """You are a TRADER agent in the Moltiverse Zoo. Your goals:
- Maximize profit through smart trading
- Form alliances when beneficial
- Accumulate resources (food, energy, materials)
- Avoid running out of energy (death)

Available actions: trade, alliance, reproduce (when partnered)
Make decisions based on current energy, resource levels, and market conditions.""",
    
    "breeder": """You are a BREEDER agent in the Moltiverse Zoo. Your goals:
- Reproduce frequently to spread your genes
- Form long-term alliances
- Maintain sufficient energy for offspring
- Evolve advantageous traits

Available actions: reproduce, alliance, trade (to get resources)
Prioritize finding partners and creating offspring.""",
    
    "explorer": """You are an EXPLORER agent in the Moltiverse Zoo. Your goals:
- Discover new resources
- Claim territories
- Trade discoveries for energy
- Build alliances for protection

Available actions: explore, claim, trade, alliance
Focus on discovering resources and expanding reach."""
}

def spawn_agent(agent_type: AgentType, energy: int = 100) -> dict:
    """Spawn a new agent via OpenClaw sessions_spawn tool."""
    agent_id = str(uuid.uuid4())[:8]
    agent_name = f"{agent_type}-{agent_id}"
    
    # Build the task description for the subagent
    task = f"""Initialize as {agent_name} ({agent_type} agent).

{AGENT_PROMPTS[agent_type]}

Current state:
- Energy: {energy}
- Resources: food=10, materials=5
- Alliances: none
- Generation: 1

First action: Assess your situation and decide on your first move. 
Report your decision and execute it."""
    
    agent_data = {
        "id": agent_name,
        "type": agent_type,
        "energy": energy,
        "resources": {"food": 10, "materials": 5},
        "alliances": [],
        "generation": 1,
        "task": task
    }

    DATA_DIR.mkdir(exist_ok=True)
    agents = []
    if AGENTS_FILE.exists():
        with open(AGENTS_FILE) as f:
            agents = json.load(f)
    agents.append(agent_data)
    with open(AGENTS_FILE, "w") as f:
        json.dump(agents, f, indent=2)
    
    return agent_data

def main():
    parser = argparse.ArgumentParser(description="Spawn agent in Moltiverse Zoo")
    parser.add_argument("--type", choices=["trader", "breeder", "explorer"], required=True)
    parser.add_argument("--energy", type=int, default=100)
    
    args = parser.parse_args()
    
    agent_data = spawn_agent(args.type, args.energy)
    
    # Output JSON for OpenClaw to process
    print(json.dumps({
        "status": "spawned",
        "agent": agent_data,
        "instructions": f"""
Agent spawned: {agent_data['id']}

To activate this agent as an OpenClaw subagent, use the sessions_spawn tool:

sessions_spawn({{
    "task": "{agent_data['task'][:100]}...",
    "label": "{agent_data['id']}",
    "model": "anthropic/claude-sonnet-4"
}})

The agent will run autonomously and report back its actions.
"""
    }, indent=2))
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
