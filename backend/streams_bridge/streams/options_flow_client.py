import asyncio
import logging
import websockets
from .config import Config
from .supabase_writer import SupabaseWriter

logger = logging.getLogger(__name__)

class OptionsFlowClient:
    def __init__(self, cfg: Config, writer: SupabaseWriter):
        self.cfg = cfg
        self.writer = writer

    async def run_forever(self):
        if not self.cfg.options_flow_url:
            logger.warning("OPTIONS_FLOW_URL not set; options flow client idle.")
            while True:
                await asyncio.sleep(30)
            return

        while True:
            try:
                headers = {}
                if self.cfg.options_flow_api_key:
                    headers['Authorization'] = f'Bearer {self.cfg.options_flow_api_key}'

                async with websockets.connect(self.cfg.options_flow_url, extra_headers=headers) as websocket:
                    logger.info("Connected to options flow stream.")
                    while True:
                        message = await websocket.recv()
                        # TODO: Map the actual payload format to the normalized dict.
                        # This is a placeholder for a single event.
                        event = {
                            "event_ts": "...",
                            "symbol": "...",
                            "option_symbol": "...",
                            "side": "...",
                            "size": 0,
                            "raw": message,
                        }
                        await self.writer.insert_options_flow([event])
            except Exception as e:
                logger.exception(f"OptionsFlowClient error: {e}")
                await asyncio.sleep(5)