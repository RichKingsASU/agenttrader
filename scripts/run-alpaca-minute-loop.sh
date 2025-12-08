#!/usr/bin/env bash
set -euo pipefail

# Ensure we are in the project root
cd "$(dirname "$0")/../" || exit 1

# --- PID Lock Guard ---
LOCK_FILE="/tmp/run-alpaca-minute-loop.pid"
if [ -e "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if ps -p "$PID" > /dev/null; then
        echo "Loop is already running with PID $PID. Exiting."
        exit 1
    else
        echo "Stale lock file found for PID $PID. Removing."
        rm -f "$LOCK_FILE"
    fi
fi
echo $$ > "$LOCK_FILE"
trap 'rm -f "$LOCK_FILE"' EXIT
# --- End Lock Guard ---

mkdir -p logs
exec 1>>logs/alpaca_stream.log 2>&1

echo "[$(date -Iseconds)] loop start (SYMS=${TASTY_SYMBOLS:-unset})"
while true; do
  echo "[$(date -Iseconds)] tick: running quotes_rest_runner.py"
  
  if python backend/streams/quotes_rest_runner.py; then
    echo "[$(date -Iseconds)] tick: quotes_rest_runner.py finished successfully"
  else
    exit_code=$?
    echo "[$(date -Iseconds)] ERROR: quotes_rest_runner.py exited with code $exit_code"
  fi
  
  echo "[$(date -Iseconds)] tick: sleeping for 60 seconds"
  sleep 60
done