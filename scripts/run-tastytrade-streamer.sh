#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[Tastytrade] Starting Tastytrade 1m streamer..."
python -m streams.tastytrade_streamer