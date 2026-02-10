#!/usr/bin/env python3
"""
Agent decision-making using LLM (Ollama or OpenAI).
"""
import argparse
import json
import os
import sys
from typing import Dict, Any

def get_llm_decision_ollama(agent_state: Dict[str, Any], model: str = "llama3.2:latest") -> Dict[str, Any]:
    """Get decision from Ollama."""
    import requests
    
    ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
    
    prompt = f"""You are an autonomous agent in the Moltiverse Zoo ecosystem.

Current state:
- Type: {agent_state['type']}
- Energy: {agent_state['energy']}
- Resources: {json.dumps(agent_state.get('resources', {}))}
- Alliances: {len(agent_state.get('alliances', []))} active
- Generation: {agent_state.get('generation', 1)}

Available actions:
1. trade: Buy/sell resources (costs energy, gains resources)
2. alliance: Form partnership (shared resources, reproductive benefits)
3. reproduce: Create offspring with partner (costs 30 energy, requires partner)
4. explore: Discover new resources (costs energy, gains resources)

Analyze your situation and choose the best action. Consider:
- Energy levels (die if energy reaches 0)
- Resource needs
- Alliance benefits
- Reproduction opportunities

Respond in JSON format:
{{
    "action": "trade|alliance|reproduce|explore",
    "reasoning": "your strategic thinking",
    "params": {{
        // action-specific parameters
    }}
}}
"""
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
        )
        response.raise_for_status()
        
        result = response.json()
        decision = json.loads(result['response'])
        return decision
        
    except Exception as e:
        return {
            "error": str(e),
            "fallback_action": "explore",
            "reasoning": "LLM unavailable, defaulting to safe explore action"
        }

def get_llm_decision_openai(agent_state: Dict[str, Any], model: str = "gpt-4") -> Dict[str, Any]:
    """Get decision from OpenAI."""
    import openai
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "error": "OPENAI_API_KEY not set",
            "fallback_action": "explore",
            "reasoning": "OpenAI unavailable"
        }
    
    openai.api_key = api_key
    
    prompt = f"""You are an autonomous agent in the Moltiverse Zoo ecosystem.

Current state:
- Type: {agent_state['type']}
- Energy: {agent_state['energy']}
- Resources: {json.dumps(agent_state.get('resources', {}))}
- Alliances: {len(agent_state.get('alliances', []))} active
- Generation: {agent_state.get('generation', 1)}

Available actions:
1. trade: Buy/sell resources
2. alliance: Form partnership
3. reproduce: Create offspring with partner (requires 30 energy + partner)
4. explore: Discover new resources

Choose the best action based on your goals as a {agent_state['type']} agent.

Respond in JSON format:
{{
    "action": "trade|alliance|reproduce|explore",
    "reasoning": "your strategic thinking",
    "params": {{}}
}}
"""
    
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an autonomous economic agent. Make strategic decisions to survive and thrive."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        decision = json.loads(response.choices[0].message.content)
        return decision
        
    except Exception as e:
        return {
            "error": str(e),
            "fallback_action": "explore",
            "reasoning": "OpenAI error, defaulting to safe action"
        }

def main():
    parser = argparse.ArgumentParser(description="Get LLM decision for agent")
    parser.add_argument("--agent-state", type=json.loads, required=True, help="Agent state JSON")
    parser.add_argument("--provider", choices=["ollama", "openai"], default="ollama")
    parser.add_argument("--model", help="Model name (e.g., llama3.2, gpt-4)")
    
    args = parser.parse_args()
    
    if args.provider == "ollama":
        model = args.model or "llama3.2:latest"
        decision = get_llm_decision_ollama(args.agent_state, model)
    else:
        model = args.model or "gpt-4"
        decision = get_llm_decision_openai(args.agent_state, model)
    
    print(json.dumps(decision, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
