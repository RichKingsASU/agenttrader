import asyncio
import logging
from .config import Config
from .supabase_writer import SupabaseWriter

logger = logging.getLogger(__name__)

class AccountUpdatesClient:
    def __init__(self, cfg: Config, writer: SupabaseWriter):
        self.cfg = cfg
        self.writer = writer

    async def run_forever(self):
        while True:
            try:
                # TODO: Wire this to the actual Developer Console WebSocket/API endpoint.
                logger.info("stream_bridge: account updates client placeholder")
                await asyncio.sleep(10)
            except Exception as e:
                logger.exception(f"AccountUpdatesClient error: {e}")
                await asyncio.sleep(5)
