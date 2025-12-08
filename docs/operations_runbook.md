## Strategy Engine – Operations

This section details how to run and configure the Strategy Engine.

### Running Locally

To run the Strategy Engine locally:

1.  **Set Environment Variables**: `export DATABASE_URL="..."`, `export STRATEGY_NAME="naive_flow_trend"`, etc.
2.  **Run in Dry-Run Mode**: `python -m backend.strategy_engine.driver`
3.  **Run with Live Paper Trading**: `python -m backend.strategy_engine.driver --execute`

### Running in a Container (Cloud Run Job)

Refer to the helper scripts:
-   `Dockerfile.strategy_engine`
-   `cloudbuild_strategy_engine.yaml`
-   `scripts/setup_cloud_run_strategy_engine.sh`

### Pre-Market Checklist

-   **Confirm Risk Limits**: `psql "$DATABASE_URL" -c "SELECT * FROM public.strategy_limits;"`
-   **Confirm Active Strategy**: `psql "$DATABASE_URL" -c "SELECT * FROM public.strategy_definitions WHERE is_active = true;"`
-   **Check Last Run**: `psql "$DATABASE_URL" -c "SELECT * FROM public.strategy_state ORDER BY trading_date DESC, updated_at DESC LIMIT 1;"`
-   **Check for Runaway Trades**: `psql "$DATABASE_URL" -c "SELECT * FROM public.strategy_state WHERE trading_date = CURRENT_DATE;"`