#!/bin/bash
# Quick start script for Moltiverse Zoo on OpenClaw

set -e

echo "🦞 Moltiverse Zoo - OpenClaw Setup"
echo "=================================="
echo ""

# Check if in openclaw directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Run this from the openclaw directory"
    exit 1
fi

# Check for pnpm
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm not found. Install with: npm install -g pnpm"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing OpenClaw dependencies..."
    pnpm install
fi

# Build if needed
if [ ! -d "dist" ]; then
    echo "🔨 Building OpenClaw..."
    pnpm build
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 not found. Install Python 3.11+"
    exit 1
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install --quiet web3 requests 2>/dev/null || pip install --quiet web3 requests

# Check environment variables
echo ""
echo "🔧 Checking environment..."
if [ -z "$MONAD_PRIVATE_KEY" ]; then
    echo "⚠️  MONAD_PRIVATE_KEY not set (optional for testing)"
fi

if [ -z "$OPENAI_API_KEY" ] && ! command -v ollama &> /dev/null; then
    echo "⚠️  No LLM configured (OPENAI_API_KEY or Ollama)"
    echo "   Install Ollama: https://ollama.com"
fi

# Create config if doesn't exist
CONFIG_DIR="$HOME/.openclaw"
CONFIG_FILE="$CONFIG_DIR/openclaw.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "📝 Creating OpenClaw config..."
    mkdir -p "$CONFIG_DIR"
    cp openclaw-zoo.json "$CONFIG_FILE"
    echo "   Config created at: $CONFIG_FILE"
else
    echo "✅ Config exists: $CONFIG_FILE"
fi

# Make skill scripts executable
echo "🔧 Setting up skills..."
chmod +x skills/moltiverse-zoo/*.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Quick Commands:"
echo "  Start gateway:  pnpm openclaw gateway --port 18789 --verbose"
echo "  Spawn agent:    python3 skills/moltiverse-zoo/spawn_agent.py --type trader --energy 100"
echo "  Check status:   python3 skills/moltiverse-zoo/ecosystem_status.py"
echo ""
echo "📖 Read MOLTIVERSE_ZOO_README.md for full documentation"
echo ""

# Optional: Start Ollama if available
if command -v ollama &> /dev/null; then
    echo "💡 Tip: Ollama detected. Pull a model with:"
    echo "   ollama pull llama3.2"
    echo ""
fi
