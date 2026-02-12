---
name: moltiverse-zoo
description: "Multi-agent economic ecosystem for Moltiverse Hackathon. Spawn autonomous agents (traders, breeders, explorers) that interact on Monad blockchain via nad.fun tokens."
metadata:
  {
    "openclaw":
      {
        "emoji": "🦞",
        "requires": { "bins": ["python3"], "config": ["agents.list"] },
        "primaryEnv": "MONAD_PRIVATE_KEY",
        "install":
          [
            {
              "id": "python",
              "kind": "download",
              "url": "https://www.python.org/downloads/",
              "label": "Install Python 3.11+",
            },
          ],
      },
  }
---

# Moltiverse Zoo - Multi-Agent Economic Ecosystem

Spawn autonomous AI agents that trade, breed, explore, and collaborate in an economic simulation on Monad blockchain.

## Overview

This skill enables OpenClaw to manage a zoo of autonomous agents:

- **Traders**: Buy/sell resources, form alliances, execute trades
- **Breeders**: Reproduce, pass traits, evolve over generations
- **Explorers**: Discover resources, claim territories

Each agent is an OpenClaw subagent with its own decision-making loop powered by LLMs.

## Core Commands

### Spawn an Agent

```bash
python3 {baseDir}/spawn_agent.py --type trader --energy 100
python3 {baseDir}/spawn_agent.py --type breeder --energy 80
python3 {baseDir}/spawn_agent.py --type explorer --energy 120
```

### Get Ecosystem Status

```bash
python3 {baseDir}/ecosystem_status.py
```

### Execute Agent Action

```bash
# Trade
python3 {baseDir}/agent_action.py --agent-id <id> --action trade --params '{"resource":"food","amount":10,"price":5}'

# Form alliance
python3 {baseDir}/agent_action.py --agent-id <id> --action alliance --params '{"partner_id":"<partner>"}'

# Reproduce
python3 {baseDir}/agent_action.py --agent-id <id> --action reproduce --params '{"partner_id":"<partner>"}'
```

## Monad Blockchain Integration

### Deploy Token on nad.fun

```bash
python3 {baseDir}/nadfun_deploy.py \
  --name "Zoo Token" \
  --symbol "ZOO" \
  --image-path ./token_image.png \
  --description "Moltiverse Zoo ecosystem token"
```

### Check Token Balance

```bash
python3 {baseDir}/check_balance.py --address <wallet> --token <token_address>
```

## Environment Setup

Required environment variables:

- `MONAD_PRIVATE_KEY`: Wallet private key for on-chain operations
- `MONAD_RPC_URL`: RPC endpoint (default: https://rpc.monad.xyz)
- `NADFUN_API_URL`: nad.fun API endpoint (default: https://dev-api.nad.fun)
- `OLLAMA_API_URL`: Ollama endpoint for agent decisions (optional)
- `OPENAI_API_KEY`: OpenAI API key for agent decisions (optional)

## Agent Decision Flow

1. Agent receives state (energy, resources, alliances)
2. LLM evaluates options and chooses action
3. Action executes (trade, alliance, reproduce, etc.)
4. Result broadcasts to OpenClaw main session
5. Ecosystem state updates

## Multi-Agent Coordination

Agents can:

- Form alliances (shared resource pools)
- Trade resources (food, energy, materials)
- Reproduce (offspring inherit traits)
- Evolve (traits mutate over generations)
- Compete for resources

Use OpenClaw's `sessions_spawn` tool to create subagents for each zoo agent.

## Data Storage

- Agent state: `{baseDir}/data/agents.json`
- Resources: `{baseDir}/data/resources.json`
- Transactions: `{baseDir}/data/transactions.json`
- ChromaDB vectors: `{baseDir}/data/chroma/`

## Notes

- Each agent runs as an OpenClaw subagent (isolated session)
- Decisions use Ollama (local) or OpenAI (API)
- Blockchain operations require Monad testnet MON tokens
- Get testnet tokens: `POST https://agents.devnads.com/v1/faucet`
