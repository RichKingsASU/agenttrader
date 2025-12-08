import asyncio
import os
import json
from datetime import datetime, timezone
from backend.streams_bridge.supabase_writer import SupabaseWriter
from backend.streams_bridge.config import load_config
from backend.streams_bridge.mapping import (
    map_devconsole_news,
    map_devconsole_options_flow,
    map_devconsole_account_update
)

async def main():
    """
    Local smoke test for the Stream Bridge: loads fixtures, maps them, and writes to Supabase.
    """
    print("Running Stream Bridge local test harness...")
    cfg = load_config()
    writer = await SupabaseWriter.create(cfg.database_url)

    # --- Test News Events ---
    print("Testing news events...")
    with open("backend/streams_bridge/fixtures/news_sample.json", 'r') as f:
        news_payload = json.load(f)
    news_event = map_devconsole_news(news_payload)
    await writer.insert_news_events([news_event])
    print("  Inserted 1 sample news event.")

    # --- Test Options Flow ---
    print("Testing options flow...")
    with open("backend/streams_bridge/fixtures/options_flow_sample.json", 'r') as f:
        options_flow_payload = json.load(f)
    options_flow_event = map_devconsole_options_flow(options_flow_payload)
    await writer.insert_options_flow([options_flow_event])
    print("  Inserted 1 sample options flow event.")

    # --- Test Account Updates ---
    print("Testing account updates...")
    with open("backend/streams_bridge/fixtures/account_update_sample.json", 'r') as f:
        account_update_payload = json.load(f)
    positions, balances, account_meta = map_devconsole_account_update(account_update_payload)

    # For account updates, first ensure the broker_account exists
    broker = account_meta['broker']
    external_account_id = account_meta['external_account_id']
    async with writer.pool.acquire() as conn:
        broker_account_id = await conn.fetchval(
            """
            INSERT INTO public.broker_accounts (broker, external_account_id, label)
            VALUES ($1, $2, $3)
            ON CONFLICT (broker, external_account_id) DO UPDATE SET label = EXCLUDED.label
            RETURNING id
            """,
            broker, external_account_id, f"{broker}-{external_account_id}"
        )

    # Add broker_account_id to positions and balances
    for p in positions:
        p['broker_account_id'] = broker_account_id
    for b in balances:
        b['broker_account_id'] = broker_account_id

    await writer.upsert_positions(positions)
    await writer.upsert_balances(balances)
    print("  Upserted sample positions and balances.")

    print("Stream Bridge local test harness finished successfully.")

if __name__ == "__main__":
    # Ensure DATABASE_URL is set
    if "DATABASE_URL" not in os.environ:
        print("Error: DATABASE_URL environment variable not set.")
    else:
        asyncio.run(main())
