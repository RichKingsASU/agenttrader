#!/usr/bin/env bash
set -euo pipefail

# Always run from repo root
cd "$(dirname "$0")/.."

echo "[tastytrade-streamer] Activating venv..."
source .venv/bin/activate

echo "[tastytrade-streamer] Using DATABASE_URL=${DATABASE_URL:-not-set}"
echo "[tastytrade-streamer] Streaming symbols: ${TASTY_SYMBOLS:-SPY,IWM}"

python backend/streams/tastytrade_streamer.py
