#!/usr/bin/env bash
set -e

# Kill any existing uvicorn processes so ports 8001/8002 are free
pkill -f "uvicorn" 2>/dev/null || true

export DATABASE_URL="postgresql://postgres:pIPWNq6LAz2hOBaQ@db.nugswladoficdyvygstg.supabase.co:5432/postgres?sslmode=require"

# Activate venv from project root
source .venv/bin/activate

# Strategy on 8001
uvicorn backend.strategy_service.app:app --host 0.0.0.0 --port 8001 &
STRAT_PID=$!

# Risk on 8002
uvicorn backend.risk_service.app:app --host 0.0.0.0 --port 8002 &
RISK_PID=$!

echo "Strategy service PID: $STRAT_PID"
echo "Risk service PID: $RISK_PID"

trap "echo 'Stopping...'; kill $STRAT_PID $RISK_PID 2>/dev/null || true" SIGINT SIGTERM

wait
