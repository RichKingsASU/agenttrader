

## Implementation Status (2025-12-08)

- **Client Implementation**: The `OptionsFlowClient` and `AccountUpdatesClient` have been implemented with safe-idle behavior.
- **UI Widgets**: New widgets for `news_events`, `options_flow`, and `broker_positions` have been added to the frontend.
- **Deployment Scaffolding**: `Dockerfile.stream_bridge`, `cloudbuild_stream_bridge.yaml`, and `scripts/setup_cloud_run_stream_bridge.sh` have been created to provide a deployment path for the Stream Bridge service.
- **Next Steps**: The primary remaining task is to provide the actual Developer Console URLs and API keys as environment variables to activate the stream clients.
