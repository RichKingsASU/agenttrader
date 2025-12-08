#!/usr/bin/env bash
set -euo pipefail
exec 1>>logs/alpaca_stream.log 2>&1
echo "[$(date -Iseconds)] loop start (DAYS=${ALPACA_BACKFILL_DAYS:-unset}, SYMS=${TASTY_SYMBOLS:-unset})"
while true; do
  echo "[$(date -Iseconds)] tick: running quotes_rest_runner.py"
  python backend/streams/quotes_rest_runner.py || echo "[$(date -Iseconds)] ERROR exitcode=$?"
  sleep 60
done
