#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"/..

echo "[Alpaca] Starting Alpaca 1m streamer..."
python -m streams.alpaca_streamer