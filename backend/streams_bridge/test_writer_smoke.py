import asyncio
import os
from datetime import datetime, timezone
from backend.streams_bridge.supabase_writer import SupabaseWriter
from backend.streams_bridge.config import load_config

async def main():
    """Smoke test for the SupabaseWriter."""
    print("Running SupabaseWriter smoke test...")
    cfg = load_config()
    writer = await SupabaseWriter.create(cfg.database_url)

    test_event = {
        "event_ts": datetime.now(timezone.utc),
        "source": "dev_console_test",
        "symbol": "SPY",
        "headline": "Stream Bridge smoke test headline",
        "body": "This is only a local smoke test.",
        "url": None,
        "category": "test",
        "sentiment": "neutral",
        "importance": 1,
        "raw": {"example": True}
    }

    try:
        await writer.insert_news_events([test_event])
        print("Smoke test successful: inserted 1 news event.")
    except Exception as e:
        print(f"Smoke test failed: {e}")

if __name__ == "__main__":
    # Ensure DATABASE_URL is set
    if "DATABASE_URL" not in os.environ:
        print("Error: DATABASE_URL environment variable not set.")
    else:
        asyncio.run(main())
