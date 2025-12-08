

## Strategy Engine – Operations

### Local Execution

To run the strategy engine locally for testing and debugging, use the following commands from the root of the repository:

**Dry-Run Mode (no trades executed):**

```bash
export DATABASE_URL='your-supabase-database-url'
python3 -m backend.strategy_engine.driver
```

**Execute Trades (places paper trades):**

```bash
export DATABASE_URL='your-supabase-database-url'
python3 -m backend.strategy_engine.driver --execute
```

### Cloud Run Execution

The strategy engine is designed to be deployed as a containerized service on Google Cloud Run. The deployment process is automated using Cloud Build and the deployment script.

### Pre-Market Checklist

Before the market opens, perform the following checks to ensure the strategy engine is ready for the trading day:

- **Verify Strategy Definitions and Limits:** Connect to the Supabase database and verify that the `strategy_definitions` and `strategy_limits` tables contain the correct entries for the active strategies.
- **Verify Strategy State:** Check the `strategy_state` table for the current trading day. There should be a row for each active strategy with `trades_placed` and `notional_traded` set to 0.
- **Verify No Runaway Trades:** Check the `strategy_logs` table for any unusual activity from the previous trading day.
