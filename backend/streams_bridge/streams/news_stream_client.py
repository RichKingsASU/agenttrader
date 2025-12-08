import asyncio
import logging
import websockets
from .config import Config
from .supabase_writer import SupabaseWriter

logger = logging.getLogger(__name__)

class NewsStreamClient:
    def __init__(self, cfg: Config, writer: SupabaseWriter):
        self.cfg = cfg
        self.writer = writer

    async def run_forever(self):
        if not self.cfg.news_stream_url:
            logger.warning("NEWS_STREAM_URL not set; news stream client idle.")
            while True:
                await asyncio.sleep(30)
            return

        while True:
            try:
                async with websockets.connect(self.cfg.news_stream_url) as websocket:
                    logger.info("Connected to news stream.")
                    # TODO: Add authentication logic here if required by the Developer Console.
                    # e.g., await websocket.send(json.dumps({"action": "auth", "key": self.cfg.news_stream_api_key}))

                    while True:
                        message = await websocket.recv()
                        # TODO: Map the actual payload format to the normalized dict.
                        # This is a placeholder for a single event.
                        event = {
                            "event_ts": "...",
                            "source": "dev_console_news",
                            "symbol": "...",
                            "headline": "...",
                            "raw": message,
                        }
                        await self.writer.insert_news_events([event])
            except Exception as e:
                logger.exception(f"NewsStreamClient error: {e}")
                await asyncio.sleep(5)