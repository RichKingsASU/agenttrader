#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Start Alpaca & Tastytrade in the background
./scripts/run-alpaca-streamer.sh 2>&1 | tee logs/alpaca_stream.log &
ALPACA_PID=$!

./scripts/run-tastytrade-streamer.sh 2>&1 | tee logs/tastytrade_stream.log &
TASTY_PID=$!

echo "Alpaca PID: $ALPACA_PID"
echo "Tastytrade PID: $TASTY_PID"
echo "Streams started. Use 'ps aux | grep streamer' or kill PIDs to stop."