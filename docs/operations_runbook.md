

### Strategy Engine – Operations

**Local Execution**

- **Dry-Run:** `python3 -m backend.strategy_engine.driver`
- **Execute:** `python3 -m backend.strategy_engine.driver --execute`

**Cloud Execution**

- **Manual Trigger:** `gcloud run jobs execute agenttrader-strategy-engine --region us-central1`
- **Check Logs:** `gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=agenttrader-strategy-engine" --project=agenttrader-prod --limit=100`

**Pre-Market Checklist**

- Confirm limits in `public.strategy_limits`.
- Confirm `strategy_state` is ready for the current day.
- Confirm Cloud Run Job `agenttrader-strategy-engine` is deployed and healthy.
- Confirm Cloud Scheduler job `agenttrader-strategy-engine-scheduler` is created and enabled.
