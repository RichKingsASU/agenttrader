#!/usr/bin/env bash
set -euo pipefail

echo "[bootstrap] Activating venv..."
source .venv/bin/activate

echo "[bootstrap] Skipping supabase db push (remote DB already migrated)"
# Temporarily disabled because CLI config parsing is broken on this machine.
# If we need migrations later, we’ll run `supabase db push` manually.
# supabase db push




echo "[bootstrap] Activating venv..."
cd "$(dirname "$0")/.."
source .venv/bin/activate

echo "[bootstrap] Ensuring Supabase migrations are pushed..."
supabase db push

echo "[bootstrap] Killing any old uvicorn processes..."
pkill -f "uvicorn" || true

echo "[bootstrap] Starting backend dev servers..."
nohup ./scripts/run-backend-dev.sh > backend.log 2>&1 &

echo "[bootstrap] Starting dummy market data streamer..."
nohup python scripts/stream_dummy_market_data.py > stream.log 2>&1 &

echo "[bootstrap] All services started."
echo " - Strategy + risk services via run-backend-dev.sh"
echo " - Dummy market ticks into Supabase via stream_dummy_market_data.py"
