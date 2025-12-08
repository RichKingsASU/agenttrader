#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "[agents] Activating venv..."
source .venv/bin/activate

echo "[agents] Running GitHub sync (daily-git-sync.sh)..."
./daily-git-sync.sh

echo "[agents] Running bootstrap_agenttrader.sh (backends + dummy market streamer)..."
./scripts/bootstrap_agenttrader.sh

echo "[agents] Starting Tastytrade streamer..."
./scripts/run-tastytrade-streamer.sh

echo "[agents] All agents completed."
