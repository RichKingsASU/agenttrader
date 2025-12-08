# AgentTrader Operations Runbook

This document outlines operational procedures for the AgentTrader system.

## Stream Bridge – Dev Console Streams

This section details how to run and configure the Stream Bridge microservice, which connects to Developer Console (e.g., Polygon, OPRA, Benzinga, TD Ameritrade) streams.

### Environment Variables Required

To activate specific stream clients, the corresponding environment variables must be set. If an `_URL` variable is not set, the respective client will idle gracefully.

- `DATABASE_URL`: (Required) Connection string for the Supabase PostgreSQL database.
- `NEWS_STREAM_URL`: (Optional) WebSocket URL for the news stream.
- `NEWS_STREAM_API_KEY`: (Optional) API key for authenticating to the news stream.
- `OPTIONS_FLOW_URL`: (Optional) WebSocket URL for the options flow stream.
- `OPTIONS_FLOW_API_KEY`: (Optional) API key for authenticating to the options flow stream.
- `ACCOUNT_UPDATES_URL`: (Optional) WebSocket URL for the account updates stream.
- `ACCOUNT_UPDATES_API_KEY`: (Optional) API key for authenticating to the account updates stream.

### Running Locally

To run the Stream Bridge locally in your Cloud Shell or development environment:

1.  **Set Environment Variables**: Export the required environment variables in your shell (e.g., `export NEWS_STREAM_URL="wss://..."`).
2.  **Navigate to Project Root**: `cd ~/agenttrader`
3.  **Start the Service**: `python -m backend.streams_bridge.main`

To stop, use `Ctrl+C`.

### Running in a Container (Cloud Run Service)

To deploy the Stream Bridge as a Cloud Run Service, refer to the helper scripts:

-   `Dockerfile.stream_bridge`: Defines the container image.
-   `cloudbuild_stream_bridge.yaml`: Configuration for Google Cloud Build.
-   `scripts/setup_cloud_run_stream_bridge.sh`: Contains commented `gcloud` commands for building the image and deploying the Cloud Run Service.

**Required IAM Roles for Deployment**: The user deploying needs `Cloud Build Editor`, `Cloud Run Admin`, and `IAM Service Account User` roles.

## Pre-Market Checklist

Before market open, perform the following checks:

-   **Alpaca Ingestion Process**: Confirm `scripts/run-alpaca-minute-loop.sh` is running. Check `ps -ef | grep run-alpaca-minute-loop | grep -v grep`.
-   **Stream Bridge Service**: If deployed, confirm the Stream Bridge service is running (locally or on Cloud Run). Check `ps -ef | grep backend/streams_bridge/main | grep -v grep` for local, or `gcloud run services describe agenttrader-stream-bridge --region=us-central1` for Cloud Run.
-   **Data Arrival (Post-Market Open)**: After market opens, verify data is arriving in Supabase:
    -   `psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.news_events WHERE received_at > NOW() - INTERVAL '5 minutes';"`
    -   `psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.options_flow WHERE received_at > NOW() - INTERVAL '5 minutes';"`
    -   `psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM public.broker_positions WHERE updated_at > NOW() - INTERVAL '5 minutes';"`
-   **UI Confirmation**: Ensure the Lovable/NextJS dashboard (`frontend/agenttrader-ui`) shows live market bars, news, options flow, and broker positions/balances.

## Safe Rollback / Disable Streams

To temporarily disable Stream Bridge clients or roll back:

-   **Stop Stream Bridge Service**: Kill the local process (Ctrl+C) or stop the Cloud Run service.
-   **Unset Environment Variables**: Unset the `_URL` environment variables (e.g., `unset NEWS_STREAM_URL`) to force clients into idle mode without stopping the service.
-   **Confirm Alpaca-Only**: Verify the Alpaca-only ingestion and paper trading system still functions as expected.
