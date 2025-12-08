

## Phase 5 – Deployment & Limits

### Strategy Limits Configuration

The `naive_flow_trend` strategy is configured with the following default limits, seeded from `supabase/sql/seed_strategy_limits.sql`:

- **Max Daily Trades:** 5
- **Max Position Size:** 1
- **Max Notional Per Trade:** 10000
- **Max Notional Per Day:** 30000
- **Max Open Positions:** 1
- **Cool Down Minutes:** 5

### Cloud Deployment

The Strategy Engine is deployed as a Google Cloud Run Job, triggered by a Cloud Scheduler job.

- **Cloud Run Job:** The job is defined in `cloudbuild_strategy_engine.yaml` and deployed using the script in `scripts/setup_cloud_run_strategy_engine.sh`.
- **Cloud Scheduler:** The scheduler is configured to run the job every 5 minutes during market hours. The configuration is in `scripts/setup_cloud_run_strategy_engine.sh`.

### Local vs. Cloud Execution

- **Local:** The strategy can be run locally for testing and development. The `driver.py` script can be run in either dry-run or execute mode.
- **Cloud:** In the cloud, the strategy is run in execute mode by default.
