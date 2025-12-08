import asyncio
import logging
import websockets
import json
from datetime import datetime, timezone
from .config import Config
from .supabase_writer import SupabaseWriter
from ..mapping import map_devconsole_news

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
                headers = {}
                if self.cfg.news_stream_api_key:
                    headers['Authorization'] = f'Bearer {self.cfg.news_stream_api_key}'

                async with websockets.connect(self.cfg.news_stream_url, extra_headers=headers) as websocket:
                    logger.info("Connected to news stream.")
                    while True:
                        message = await websocket.recv()
                        payload = json.loads(message)
                        event = map_devconsole_news(payload)
                        await self.writer.insert_news_events([event])
            except Exception as e:
                logger.exception(f"NewsStreamClient error: {e}")
                await asyncio.sleep(5)
