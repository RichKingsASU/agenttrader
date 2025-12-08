#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
echo "[tastytrade-rest] DB: ${DATABASE_URL:-not-set}"
echo "[tastytrade-rest] Symbols: ${TASTY_SYMBOLS:-SPY,IWM}"
python backend/streams/tastytrade_rest_poll_streamer.py
