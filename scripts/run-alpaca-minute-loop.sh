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

export DATABASE_URL='postgresql://postgres:TUM3T8FiHEEFKoGu@db.nugswladoficdyvygstg.supabase.co:6543/postgres?sslmode=require'
export ALPACA_KEY_ID='PKM67H5TC73LYKRTEWX3ANR2BW'
export ALPACA_SECRET_KEY='HAe6wPgor1xpGT6QvfbY6BP7faZTbr9HR64MEXkEAH89'
export APCA_API_KEY_ID='PKM67H5TC73LYKRTEWX3ANR2BW'
export APCA_API_SECRET_KEY='HAe6wPgor1xpGT6QvfbY6BP7faZTbr9HR64MEXkEAH89'
export TASTY_SYMBOLS='SPY,IWM,QQQ'
export ALPACA_DATA_HOST='https://data.alpaca.markets'
export ALPACA_BACKFILL_DAYS='10'
export ALPACA_FEED='iex'

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