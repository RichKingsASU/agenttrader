import asyncio
import logging
import websockets
import json
from datetime import datetime, timezone
from .config import Config
from .supabase_writer import SupabaseWriter
from ..mapping import map_devconsole_account_update

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
                        payload = json.loads(message)
                        positions, balances, account_meta = map_devconsole_account_update(payload)

                        # Ensure broker_accounts row exists and get its ID
                        async with self.writer.pool.acquire() as conn:
                            broker_account_id = await conn.fetchval(
                                """
                                INSERT INTO public.broker_accounts (broker, external_account_id, label)
                                VALUES ($1, $2, $3)
                                ON CONFLICT (broker, external_account_id) DO UPDATE SET label = EXCLUDED.label
                                RETURNING id
                                """,
                                account_meta['broker'], account_meta['external_account_id'], f"{account_meta['broker']}-{account_meta['external_account_id']}"
                            )

                        # Add broker_account_id to positions and balances
                        for p in positions:
                            p['broker_account_id'] = broker_account_id
                        for b in balances:
                            b['broker_account_id'] = broker_account_id

                        await self.writer.upsert_positions(positions)
                        await self.writer.upsert_balances(balances)

            except Exception as e:
                logger.exception(f"AccountUpdatesClient error: {e}")
                await asyncio.sleep(5)
