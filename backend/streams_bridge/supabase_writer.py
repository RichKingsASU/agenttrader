import asyncio
import logging
import asyncpg
from .config import Config

logger = logging.getLogger(__name__)

class SupabaseWriter:
    def __init__(self, pool):
        self.pool = pool

    @classmethod
    async def create(cls, database_url: str):
        pool = await asyncpg.create_pool(database_url)
        return cls(pool)

    async def insert_options_flow(self, events: list[dict]) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    """
                    INSERT INTO public.options_flow (event_ts, symbol, option_symbol, side, size, notional, strike, expiration, option_type, trade_price, bid, ask, venue, raw)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    """,
                    [
                        (
                            e['event_ts'], e['symbol'], e['option_symbol'], e['side'], e['size'], e.get('notional'), e.get('strike'),
                            e.get('expiration'), e.get('option_type'), e.get('trade_price'), e.get('bid'), e.get('ask'), e.get('venue'), e.get('raw')
                        ) for e in events
                    ]
                )

    async def insert_news_events(self, events: list[dict]) -> None:
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    """
                    INSERT INTO public.news_events (event_ts, source, symbol, headline, body, url, category, sentiment, importance, raw)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ON CONFLICT (source, event_ts, headline) DO NOTHING
                    """,
                    [
                        (
                            e.get('event_ts'), e['source'], e.get('symbol'), e['headline'], e.get('body'), e.get('url'),
                            e.get('category'), e.get('sentiment'), e.get('importance'), e.get('raw')
                        ) for e in events
                    ]
                )

    async def upsert_positions(self, positions: list[dict]) -> None:
        # This is a complex operation that requires getting the broker_account_id first.
        # For this scaffold, we will just log the positions.
        logger.info(f"Received {len(positions)} positions to upsert (scaffold).")

    async def upsert_balances(self, balances: list[dict]) -> None:
        # Similar to positions, this is complex and will be logged for now.
        logger.info(f"Received {len(balances)} balances to upsert (scaffold).")

