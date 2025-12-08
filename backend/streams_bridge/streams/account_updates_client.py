import asyncio
import logging
import websockets
from .config import Config
from .supabase_writer import SupabaseWriter

logger = logging.getLogger(__name__)

class AccountUpdatesClient:
    def __init__(self, cfg: Config, writer: SupabaseWriter):
        self.cfg = cfg
        self.writer = writer

    async def run_forever(self):
        if not self.cfg.account_updates_url:
            logger.warning("ACCOUNT_UPDATES_URL not set; account updates client idle.")
            while True:
                await asyncio.sleep(30)
            return

        while True:
            try:
                headers = {}
                if self.cfg.account_updates_api_key:
                    headers['Authorization'] = f'Bearer {self.cfg.account_updates_api_key}'

                async with websockets.connect(self.cfg.account_updates_url, extra_headers=headers) as websocket:
                    logger.info("Connected to account updates stream.")
                    while True:
                        message = await websocket.recv()
                        # TODO: Map the actual TD Ameritrade payload to the normalized dicts.
                        # This is a placeholder for a single event.
                        positions = [
                            # {
                            #     "broker": "td_ameritrade",
                            #     "external_account_id": "...",
                            #     "symbol": "...",
                            #     "qty": 0,
                            #     "updated_at": "...",
                            #     "raw": message
                            # }
                        ]
                        balances = [
                            # {
                            #     "broker": "td_ameritrade",
                            #     "external_account_id": "...",
                            #     "cash": 0,
                            #     "updated_at": "...",
                            #     "raw": message
                            # }
                        ]
                        await self.writer.upsert_positions(positions)
                        await self.writer.upsert_balances(balances)
            except Exception as e:
                logger.exception(f"AccountUpdatesClient error: {e}")
                await asyncio.sleep(5)