# 🦞 Moltiverse Zoo

Moltiverse Zoo is a multi‑agent ecosystem built on top of OpenClaw. It spawns traders, breeders, and explorers that compete, cooperate, and evolve while a live command center visualizes their activity with cinematic highlights, heatmaps, alliances, and replay controls.

## What’s included

- **OpenClaw‑native gateway** with a dedicated zoo profile and port.
- **Python skill suite** for spawning agents, actions, simulation loops, and status reporting.
- **Live UI command center** with cinematic spotlight, heatmap overlays, alliance graph, replay mode, and zoomable map.
- **LLM decision support** via Ollama (default) or OpenAI.

## Repository layout

- skills/moltiverse-zoo/ — Python skills, data, and UI.
- openclaw-zoo.json — Zoo gateway config (profile‑scoped).
- .env — Local secrets and defaults (not committed).

## Quick start

Follow the step‑by‑step guide in QUICKSTART.md.

Short path:

1. Run setup: ./setup-zoo.sh
2. Start the gateway: pnpm openclaw --profile zoo gateway --port 18790 --verbose
3. Spawn agents: python3 skills/moltiverse-zoo/spawn_agent.py ...
4. Start the UI: python3 skills/moltiverse-zoo/serve_ui.py --port 8787

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
