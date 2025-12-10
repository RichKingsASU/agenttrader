# AgentTrader Runbook

This runbook provides essential information for operating and maintaining the AgentTrader system.

## 1. Ingestion Loop Management

### Start Ingestion Loop (Cloud Shell)
To start the minute-bar ingestion loop in the background, run:
```bash
nohup ./scripts/run-alpaca-minute-loop.sh >/dev/null 2>&1 &
```

### Stop Ingestion Loop
To stop any running ingestion loops, run:
```bash
pkill -f run-alpaca-minute-loop.sh || true
```

### Verify Ingestion Loop Status
To check if the ingestion loop is running, and to tail its logs:
```bash
ps -ef | grep run-alpaca-minute-loop | grep -v grep || true
tail -n 40 logs/alpaca_stream.log
```
*(Note: During off-market hours, the logs may show "no new data", which is normal.)*

## 2. Alpaca Account & Paper Trading

### Verify Alpaca Paper Account Authentication
To confirm your Alpaca paper trading API credentials are valid:
```bash
source .env.local && curl -sS -i \
    -H "APCA-API-KEY-ID: $ALPACA_KEY_ID" \
    -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY" \
    https://paper-api.alpaca.markets/v2/account
```
Expected output: HTTP 200 response.

### Place a Manual Paper Trade
To place a manual paper trade (e.g., SPY buy 1):
```bash
source .env.local && python backend/streams/manual_paper_trade.py SPY buy 1
```

### Query Paper Trades
To view recent paper trades in Supabase:
```bash
source .env.local && psql "$DATABASE_URL" -c "SELECT symbol, side, qty, price, status, source, created_at FROM public.paper_trades ORDER BY created_at DESC LIMIT 5;"
```

## 3. Supabase Data Queries

### Query Latest Market Data (public.market_data_1m)
To see the latest minute-bar data:
```bash
source .env.local && psql "$DATABASE_URL" -c "SELECT symbol, max(ts) FROM public.market_data_1m GROUP BY 1 ORDER BY 1;"
```

## 4. Lovable UI Configuration

To enable the AgentTrader dashboard in Lovable UI, you **must** set the following environment variables in your Lovable deployment:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

The dashboard will then display system health, real-time market data, and paper trade history.

## 5. Cloud Run & Cloud Scheduler Helpers

Helper scripts are provided to set up ingestion on Cloud Run and Cloud Scheduler. These scripts contain commented `gcloud` commands and notes on required IAM roles. You must execute these commands manually in your GCP environment:

- `scripts/setup_cloud_run_ingest.sh`
- `scripts/setup_cloud_scheduler_ingest.sh`

Ensure you have the necessary IAM permissions before running them.

## 6. Strategy Engine

The naive strategy driver is located at `backend/strategy/naive_strategy_driver.py`.

### Run Strategy in Dry-Run Mode
```bash
source .env.local && python backend/strategy/naive_strategy_driver.py
```

### Run Strategy with Trade Execution
*(Only if Alpaca paper trading credentials are valid)*
```bash
source .env.local && python backend/strategy/naive_strategy_driver.py --execute
```
