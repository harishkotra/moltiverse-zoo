#!/usr/bin/env python3
"""
Execute agent actions: trade, alliance, reproduce, explore.
"""
import argparse
import json
import sys
import time
import random
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path(__file__).parent / "data"

def load_agents() -> list:
    """Load agents from data file."""
    agents_file = DATA_DIR / "agents.json"
    if not agents_file.exists():
        return []
    with open(agents_file) as f:
        return json.load(f)

def save_agents(agents: list):
    """Save agents to data file."""
    DATA_DIR.mkdir(exist_ok=True)
    agents_file = DATA_DIR / "agents.json"
    with open(agents_file, 'w') as f:
        json.dump(agents, f, indent=2)

def log_transaction(transaction: Dict[str, Any]):
    """Log a transaction."""
    transactions_file = DATA_DIR / "transactions.json"
    transactions = []
    if transactions_file.exists():
        with open(transactions_file) as f:
            transactions = json.load(f)
    
    transaction["timestamp"] = int(time.time())
    transactions.append(transaction)
    
    with open(transactions_file, 'w') as f:
        json.dump(transactions, f, indent=2)

def execute_trade(agent_id: str, params: dict) -> dict:
    """Execute a trade action."""
    agents = load_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)
    
    if not agent:
        return {"status": "error", "error": "Agent not found"}
    
    resource = params.get("resource")
    amount = params.get("amount", 0)
    price = params.get("price", 0)
    
    # Simple trade logic
    if agent["energy"] < amount * price:
        return {"status": "error", "error": "Insufficient energy"}
    
    agent["energy"] -= amount * price
    agent["resources"][resource] = agent["resources"].get(resource, 0) + amount
    
    save_agents(agents)
    log_transaction({
        "type": "trade",
        "agent_id": agent_id,
        "resource": resource,
        "amount": amount,
        "price": price
    })
    
    return {
        "status": "success",
        "action": "trade",
        "agent_id": agent_id,
        "result": f"Traded {amount} {resource} for {amount * price} energy",
        "new_energy": agent["energy"]
    }

def execute_alliance(agent_id: str, params: dict) -> dict:
    """Form an alliance between two agents."""
    agents = load_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)
    partner_id = params.get("partner_id")
    partner = next((a for a in agents if a["id"] == partner_id), None)
    
    if not agent or not partner:
        return {"status": "error", "error": "Agent or partner not found"}
    
    if partner_id in agent.get("alliances", []):
        return {"status": "error", "error": "Alliance already exists"}
    
    agent.setdefault("alliances", []).append(partner_id)
    partner.setdefault("alliances", []).append(agent_id)
    
    save_agents(agents)
    log_transaction({
        "type": "alliance",
        "agent_id": agent_id,
        "partner_id": partner_id
    })
    
    return {
        "status": "success",
        "action": "alliance",
        "agent_id": agent_id,
        "partner_id": partner_id,
        "result": f"Alliance formed between {agent_id} and {partner_id}"
    }

def execute_reproduce(agent_id: str, params: dict) -> dict:
    """Reproduce - create offspring with traits from both parents."""
    agents = load_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)
    partner_id = params.get("partner_id")
    partner = next((a for a in agents if a["id"] == partner_id), None)
    
    if not agent or not partner:
        return {"status": "error", "error": "Agent or partner not found"}
    
    # Check energy cost
    reproduction_cost = 30
    if agent["energy"] < reproduction_cost or partner["energy"] < reproduction_cost:
        return {"status": "error", "error": "Insufficient energy for reproduction"}
    
    # Create offspring
    import uuid
    offspring_id = f"{agent['type']}-{str(uuid.uuid4())[:8]}"
    offspring = {
        "id": offspring_id,
        "type": agent["type"],
        "energy": 50,
        "resources": {"food": 5, "materials": 2},
        "alliances": [],
        "generation": agent.get("generation", 1) + 1,
        "parents": [agent_id, partner_id]
    }
    
    # Deduct energy
    agent["energy"] -= reproduction_cost
    partner["energy"] -= reproduction_cost
    
    agents.append(offspring)
    save_agents(agents)
    
    log_transaction({
        "type": "reproduce",
        "agent_id": agent_id,
        "partner_id": partner_id,
        "offspring_id": offspring_id
    })
    
    return {
        "status": "success",
        "action": "reproduce",
        "agent_id": agent_id,
        "partner_id": partner_id,
        "offspring": offspring,
        "result": f"Offspring {offspring_id} created (generation {offspring['generation']})"
    }

def execute_explore(agent_id: str, params: dict) -> dict:
    """Explore to discover resources (costs energy, yields resources)."""
    agents = load_agents()
    agent = next((a for a in agents if a["id"] == agent_id), None)

    if not agent:
        return {"status": "error", "error": "Agent not found"}

    energy_cost = int(params.get("energy_cost", 5))
    if agent["energy"] < energy_cost:
        return {"status": "error", "error": "Insufficient energy"}

    food_gain = int(params.get("food_gain", random.randint(1, 5)))
    materials_gain = int(params.get("materials_gain", random.randint(0, 3)))

    agent["energy"] -= energy_cost
    agent["resources"]["food"] = agent["resources"].get("food", 0) + food_gain
    agent["resources"]["materials"] = agent["resources"].get("materials", 0) + materials_gain

    save_agents(agents)
    log_transaction({
        "type": "explore",
        "agent_id": agent_id,
        "energy_cost": energy_cost,
        "food_gain": food_gain,
        "materials_gain": materials_gain
    })

    return {
        "status": "success",
        "action": "explore",
        "agent_id": agent_id,
        "result": f"Explored: -{energy_cost} energy, +{food_gain} food, +{materials_gain} materials",
        "new_energy": agent["energy"],
        "gains": {"food": food_gain, "materials": materials_gain}
    }

def main():
    parser = argparse.ArgumentParser(description="Execute agent action")
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--action", choices=["trade", "alliance", "reproduce", "explore"], required=True)
    parser.add_argument("--params", type=json.loads, default="{}")
    
    args = parser.parse_args()
    
    if args.action == "trade":
        result = execute_trade(args.agent_id, args.params)
    elif args.action == "alliance":
        result = execute_alliance(args.agent_id, args.params)
    elif args.action == "reproduce":
        result = execute_reproduce(args.agent_id, args.params)
    elif args.action == "explore":
        result = execute_explore(args.agent_id, args.params)
    else:
        result = {"status": "error", "error": "Unknown action"}
    
    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
