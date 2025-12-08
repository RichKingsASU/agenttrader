### Strategy Engine – Operations

**Local Execution**

- **Dry-Run:** `python3 -m backend.strategy_engine.driver`
- **Execute:** `python3 -m backend.strategy_engine.driver --execute`

**Cloud Execution**

- **Manual Trigger:** `gcloud run jobs execute strategy-engine-job --region us-central1`
- **Check Logs:** `gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=strategy-engine-job" --project=agenttrader-prod --limit=100`

**Cloud Scheduler Manual Update (due to gcloud CLI issue)**

If automatic Cloud Scheduler updates fail, use the following command to manually update the schedule:

```bash
gcloud scheduler jobs update http strategy-engine-scheduler \
  --location=us-central1 \
  --schedule="*/5 14-21 * * 1-5" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/agenttrader-prod/jobs/strategy-engine-job:run" \
  --http-method="POST" \
  --oidc-service-account-email="my-run-sa@agenttrader-prod.iam.gserviceaccount.com"
```

**Pre-Market Checklist**

- Confirm limits in `public.strategy_limits`.
- Confirm `strategy_state` is ready for the current day.
- Confirm Cloud Run Job `strategy-engine-job` is deployed and healthy.
- Confirm Cloud Scheduler job `strategy-engine-scheduler` is created and enabled, and has the correct schedule (`*/5 14-21 * * 1-5`).