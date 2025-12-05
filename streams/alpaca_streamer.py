# streams/alpaca_streamer.py
import os
import asyncio
from datetime import datetime, timezone

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.live import StockDataStream
from alpaca.data.models.bars import Bar
import psycopg2
from psycopg2.extras import execute_values

ALPACA_API_KEY_ID = os.environ["ALPACA_API_KEY_ID"]
ALPACA_API_SECRET_KEY = os.environ["ALPACA_API_SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

SYMBOLS = ["SPY", "IWM"]

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

def insert_bar(conn, symbol: str, bar: Bar):
    with conn.cursor() as cur:
        # Align with your market_data_1m columns
        # Assume: ts, symbol, open, high, low, close, volume
        cur.execute(
            """
            insert into public.market_data_1m (ts, symbol, open, high, low, close, volume)
            values (%s, %s, %s, %s, %s, %s, %s)
            on conflict (ts, symbol) do update
            set open = excluded.open,
                high = excluded.high,
                low  = excluded.low,
                close = excluded.close,
                volume = excluded.volume;
            """,
            (
                bar.timestamp.replace(tzinfo=timezone.utc),
                symbol,
                float(bar.open),
                float(bar.high),
                float(bar.low),
                float(bar.close),
                float(bar.volume),
            ),
        )
    conn.commit()

async def main():
    conn = get_db_conn()
    stream = StockDataStream(ALPACA_API_KEY_ID, ALPACA_API_SECRET_KEY)

    async def on_bar(bar: Bar):
        symbol = bar.symbol
        print(f"[Alpaca] 1m bar {symbol} @ {bar.timestamp} close={bar.close}")
        insert_bar(conn, symbol, bar)

    for sym in SYMBOLS:
        stream.subscribe_bars(on_bar, sym)

    print(f"[Alpaca] Starting stream for symbols: {SYMBOLS}")
    await stream.run()

if __name__ == "__main__":
    asyncio.run(main())