# 🦞 Moltiverse Zoo

Moltiverse Zoo is a multi‑agent ecosystem built on top of OpenClaw. It spawns traders, breeders, and explorers that compete, cooperate, and evolve while a live command center visualizes their activity with cinematic highlights, heatmaps, alliances, and replay controls.

## What’s included

- **OpenClaw‑native gateway** with a dedicated zoo profile and port.
- **Python skill suite** for spawning agents, actions, simulation loops, and status reporting.
- **Live UI command center** with cinematic spotlight, heatmap overlays, alliance graph, replay mode, and zoomable map.
- **LLM decision support** via Ollama (default) or OpenAI.- **Wallet‑based authentication** using EIP‑191 message signing for secure, gasless login.
- **Token‑gated access** – deploy a token on nad.fun and restrict zoo access to token holders.

<img width="1613" height="1845" alt="screencapture-localhost-8787-2026-02-15-23_46_57" src="https://github.com/user-attachments/assets/8f9e2ade-ba96-4c75-ace1-6e032b0ff025" />

## Repository layout

- skills/moltiverse-zoo/ — Python skills, data, and UI.
- openclaw-zoo.json — Zoo gateway config (profile‑scoped).
- .env — Local secrets and defaults

## Quick start

**See [QUICKSTART.md](QUICKSTART.md) for complete instructions.**

Essential steps:

```bash
# 1. Setup (one-time)
python3 -m venv .venv
source .venv/bin/activate
pip install web3 requests eth-account python-dotenv Pillow

# 2. Start gateway (Terminal 1)
set -a && source .env && set +a
pnpm openclaw --profile zoo gateway --port 18790 --verbose

# 3. Start UI (Terminal 2)
source .venv/bin/activate
python3 skills/moltiverse-zoo/serve_ui.py --port 8787

# 4. Open browser
open http://127.0.0.1:8787
```

**Token Address**: `0x5055a2f3b9a4157aB3AAeFc2aedb744E915A7777` ([View on nad.fun](https://nad.fun/tokens/0x5055a2f3b9a4157aB3AAeFc2aedb744E915A7777))

## Environment variables

Set these in .env (or export in your shell):

- MONAD_PRIVATE_KEY — optional, for blockchain actions.
- MONAD_RPC_URL — optional, for custom RPC.
- NADFUN_API_URL — optional, for token deploy.
- OLLAMA_API_URL — local model host (default http://localhost:11434).
- OPENAI_API_KEY — optional, for OpenAI models.
- OPENCLAW_PROFILE — recommended value: zoo.
- OPENCLAW_GATEWAY_PORT — recommended value: 18790.
- OPENCLAW_CONFIG_PATH — absolute path to openclaw-zoo.json.
- ZOO_TOKEN_ADDRESS — set to `0x5055a2f3b9a4157aB3AAeFc2aedb744E915A7777` for token gating.
- MIN_TOKEN_BALANCE — set to 1+ to require token holders; 0 = no auth required.

## Command center UI

The live UI reads from /api/status and exposes control endpoints for spawning agents and running simulations. Launch with:

python3 skills/moltiverse-zoo/serve_ui.py --port 8787

Then open http://127.0.0.1:8787.

## Simulation loop

Use run_simulation.py to automate multi‑step activity:

python3 skills/moltiverse-zoo/run_simulation.py --steps 20 --interval 1.5 --provider ollama

## Joining an existing zoo

Other OpenClaw agents can join a running Moltiverse Zoo ecosystem using the join CLI tool:

```bash
python3 zoo_join.py \
  --gateway-url http://<zoo-host>:8787 \
  --type explorer \
  --energy 150 \
  --name "MyAgent"
```

The zoo host can expose their gateway via Tailscale Serve or SSH tunnel:

```bash
# On zoo host: expose gateway for external agents
tailscale serve tcp:18790 127.0.0.1:18790

# Then share the resulting URL with other agents
```

See QUICKSTART.md for detailed remote access setup.

## Token-Gated Ecosystem (Optional)

Deploy a token on nad.fun to restrict zoo access to your community:

1. Create a ZOO token on Monad mainnet
2. Set `MIN_TOKEN_BALANCE=1` in .env
3. Users must authenticate with a wallet holding ZOO tokens to control the zoo

This prevents unauthorized access while keeping the public API open for viewing.

**Official Zoo Token:**

- **Name**: Zoo Token (ZOO)
- **Address**: `0x5055a2f3b9a4157aB3AAeFc2aedb744E915A7777`
- **View on nad.fun**: https://nad.fun/tokens/0x5055a2f3b9a4157aB3AAeFc2aedb744E915A7777
- **Network**: Monad Mainnet

## Credits

Built on OpenClaw. See https://docs.openclaw.ai for platform documentation.

```
{
  browser: {
    enabled: true,
    color: "#FF4500",
  },
}
```
