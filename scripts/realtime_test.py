
import asyncio
import os
from supabase_async import create_client
import subprocess
import threading
import time

async def main():
    url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")

    supabase: Client = await create_client(url, key)

    event = threading.Event()

    def on_change(payload):
        print("Change received!", payload)
        event.set()

    channel = supabase.realtime.channel("public:live_quotes")
    channel.on("postgres_changes", {"event": "*", "schema": "public", "table": "live_quotes"}, on_change)
    await channel.subscribe()

    def run_ingest():
        print("Running ingest script...")
        time.sleep(2)
        subprocess.run(["python", "agenttrader/backend/streams/test_live_quote_ingest.py"], env=os.environ)

    ingest_thread = threading.Thread(target=run_ingest)
    ingest_thread.start()

    print("Waiting for change...")
    event.wait(timeout=15)
    ingest_thread.join()

    if not event.is_set():
        print("Test failed: No change received within the timeout period.")
    else:
        print("Test successful: Change received.")
    
    await supabase.realtime.close()
    subprocess.run(["mv", "agenttrader/.env.local.bak", "agenttrader/.env.local"])


if __name__ == "__main__":
    asyncio.run(main())
