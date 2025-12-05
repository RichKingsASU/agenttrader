#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")"

echo "[agents] Activating venv..."
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
else
  echo "[agents] ERROR: .venv not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r backend/strategy_service/requirements.txt -r backend/risk_service/requirements.txt"
  exit 1
fi

echo "[agents] Running GitHub sync (daily-git-sync.sh)..."
./daily-git-sync.sh

echo "[agents] Running bootstrap_agenttrader.sh (backends + dummy market streamer)..."
./scripts/bootstrap_agenttrader.sh

echo "[agents] All agents completed."
