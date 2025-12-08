## Implementation Phase 3 – Live Dev Console Streams (2025-12-08)

This phase focuses on making the Stream Bridge truly "live-ready" for integration with Developer Console streams. The work includes:

- **Config-level Integration**: Ensuring `config.py` and all stream clients are correctly wired to consume environment variables for Developer Console URLs and API keys (`NEWS_STREAM_URL`, `NEWS_STREAM_API_KEY`, `OPTIONS_FLOW_URL`, `OPTIONS_FLOW_API_KEY`, `ACCOUNT_UPDATES_URL`, `ACCOUNT_UPDATES_API_KEY`). Clients will log clear warnings and idle gracefully if these variables are not set.
- **Payload Mapping Functions**: Implementing explicit, well-documented mapping helpers in `backend/streams_bridge/mapping.py`. These functions will normalize raw JSON payloads from the Developer Console streams into the internal SupabaseWriter expected shapes, with robustness to missing fields.
- **Local Validation Path**: Providing local test harnesses (`backend/streams_bridge/test_stream_bridge_local.py`) that consume sample JSON payloads from local fixtures. This allows for end-to-end testing of mapping and writing to Supabase without requiring live WebSocket connections.
- **Operational Runbook**: Creating or updating `docs/operations_runbook.md` to cover starting/stopping the Stream Bridge locally and in a containerized environment, environment variable requirements, and pre-market checks.

**Non-Goals**: This phase will *not* modify existing Alpaca ingestion or paper trading functionalities. It also does *not* assume real Developer Console URLs or API keys are available during this execution, instead relying on fixtures and clear documentation for future setup.