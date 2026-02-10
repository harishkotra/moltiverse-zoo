#!/usr/bin/env python3
"""
Run an automated simulation loop for Moltiverse Zoo agents.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

from agent_action import execute_trade, execute_alliance, execute_reproduce, execute_explore
from agent_decision import get_llm_decision_ollama, get_llm_decision_openai

DATA_DIR = Path(__file__).parent / "data"
AGENTS_FILE = DATA_DIR / "agents.json"


def load_agents() -> List[Dict[str, Any]]:
    if not AGENTS_FILE.exists():
        return []
    with open(AGENTS_FILE) as f:
        return json.load(f)


def pick_partner(agent_id: str, agents: List[Dict[str, Any]]) -> str | None:
    candidates = [a["id"] for a in agents if a.get("energy", 0) > 0 and a["id"] != agent_id]
    return random.choice(candidates) if candidates else None


def build_trade_params(agent: Dict[str, Any]) -> Dict[str, Any]:
    resource = random.choice(["food", "materials"])
    amount = random.randint(1, 5)
    price = random.randint(1, 5)
    return {"resource": resource, "amount": amount, "price": price}


def decide_action(agent: Dict[str, Any], provider: str, model: str | None) -> Dict[str, Any]:
    if provider == "openai":
        decision = get_llm_decision_openai(agent, model or "gpt-4")
    else:
        decision = get_llm_decision_ollama(agent, model or "llama3.2:latest")

    if "action" not in decision:
        return {"action": "explore", "params": {}}

    return decision


def execute_action(agent: Dict[str, Any], decision: Dict[str, Any], agents: List[Dict[str, Any]]):
    action = decision.get("action")
    params = decision.get("params") or {}

    if action == "trade":
        return execute_trade(agent["id"], params or build_trade_params(agent))
    if action == "alliance":
        partner_id = params.get("partner_id") or pick_partner(agent["id"], agents)
        if not partner_id:
            return execute_explore(agent["id"], {})
        return execute_alliance(agent["id"], {"partner_id": partner_id})
    if action == "reproduce":
        partner_id = params.get("partner_id") or pick_partner(agent["id"], agents)
        if not partner_id:
            return execute_explore(agent["id"], {})
        return execute_reproduce(agent["id"], {"partner_id": partner_id})
    if action == "explore":
        return execute_explore(agent["id"], params)

    return execute_explore(agent["id"], {})


def main():
    parser = argparse.ArgumentParser(description="Run automated zoo simulation")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--interval", type=float, default=1.5)
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", help="LLM model name")

    args = parser.parse_args()

    for step in range(1, args.steps + 1):
        agents = load_agents()
        active = [a for a in agents if a.get("energy", 0) > 0]
        if not active:
            print(json.dumps({"status": "stopped", "reason": "no active agents"}, indent=2))
            return 0

        results = []
        for agent in active:
            decision = decide_action(agent, args.provider, args.model)
            result = execute_action(agent, decision, active)
            results.append({"agent": agent["id"], "decision": decision, "result": result})

        print(json.dumps({"step": step, "results": results}, indent=2))
        time.sleep(args.interval)

    return 0


if __name__ == "__main__":
    sys.exit(main())
