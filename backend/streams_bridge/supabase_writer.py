import asyncio
import logging
import json
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
        if not events:
            return
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.executemany(
                    """
                    INSERT INTO public.options_flow (event_ts, symbol, option_symbol, side, size, notional, strike, expiration, option_type, trade_price, bid, ask, venue, raw)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT (source, event_ts, option_symbol) DO NOTHING
                    """,
                    [
                        (
                            e['event_ts'], e['symbol'], e['option_symbol'], e['side'], e['size'], e.get('notional'), e.get('strike'),
                            e.get('expiration'), e.get('option_type'), e.get('trade_price'), e.get('bid'), e.get('ask'), e.get('venue'), json.dumps(e.get('raw'))
                        ) for e in events
                    ]
                )

    async def insert_news_events(self, events: list[dict]) -> None:
        if not events:
            return
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
                            e.get('category'), e.get('sentiment'), e.get('importance'), json.dumps(e.get('raw'))
                        ) for e in events
                    ]
                )

    async def upsert_positions(self, positions: list[dict]) -> None:
        if not positions:
            return
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # First, get the broker_account_id. This is a simplified example.
                # In a real system, you would likely have a cache or a more efficient way to get this.
                for p in positions:
                    broker_account_id = await conn.fetchval(
                        "SELECT id FROM public.broker_accounts WHERE broker = $1 AND external_account_id = $2",
                        p['broker'], p['external_account_id']
                    )
                    if broker_account_id:
                        await conn.execute(
                            """
                            INSERT INTO public.broker_positions (broker_account_id, symbol, qty, avg_price, market_value, updated_at, raw)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (broker_account_id, symbol) DO UPDATE SET
                                qty = EXCLUDED.qty,
                                avg_price = EXCLUDED.avg_price,
                                market_value = EXCLUDED.market_value,
                                updated_at = EXCLUDED.updated_at,
                                raw = EXCLUDED.raw
                            """,
                            broker_account_id, p['symbol'], p['qty'], p.get('avg_price'), p.get('market_value'), p['updated_at'], json.dumps(p.get('raw'))
                        )

    async def upsert_balances(self, balances: list[dict]) -> None:
        if not balances:
            return
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for b in balances:
                    broker_account_id = await conn.fetchval(
                        "SELECT id FROM public.broker_accounts WHERE broker = $1 AND external_account_id = $2",
                        b['broker'], b['external_account_id']
                    )
                    if broker_account_id:
                        await conn.execute(
                            """
                            INSERT INTO public.broker_balances (broker_account_id, cash, buying_power, maintenance_margin, equity, updated_at, raw)
                            VALUES ($1, $2, $3, $4, $5, $6, $7)
                            ON CONFLICT (broker_account_id) DO UPDATE SET
                                cash = EXCLUDED.cash,
                                buying_power = EXCLUDED.buying_power,
                                maintenance_margin = EXCLUDED.maintenance_margin,
                                equity = EXCLUDED.equity,
                                updated_at = EXCLUDED.updated_at,
                                raw = EXCLUDED.raw
                            """,
                            broker_account_id, b.get('cash'), b.get('buying_power'), b.get('maintenance_margin'), b.get('equity'), b['updated_at'], json.dumps(b.get('raw'))
                        )