import asyncio
import logging
import os
from datetime import datetime, timezone

import psycopg

from tastytrade.session import Session
from tastytrade.dxfeed import DXLinkStreamer, Quote

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DATABASE_URL = os.environ.get("DATABASE_URL")
TASTY_USER = os.environ.get("TASTY_USER")
TASTY_PASS = os.environ.get("TASTY_PASS")
SYMBOLS = [s.strip() for s in os.environ.get("TASTY_SYMBOLS", "SPY,IWM").split(",") if s.strip()]

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var is required")
if not TASTY_USER or not TASTY_PASS:
    raise RuntimeError("TASTY_USER and TASTY_PASS env vars are required")

def floor_to_minute(ts: datetime) -> datetime:
    return ts.replace(second=0, microsecond=0)

async def stream_once():
    logging.info("Connecting to Postgres...")
    conn = psycopg.connect(DATABASE_URL)
    conn.autocommit = True

    # ---- Login WITHOUT MFA args (this matches your installed package) ----
    logging.info("Creating Tastytrade session (no MFA args, relies on remembered device)...")
    session = Session(TASTY_USER, TASTY_PASS)  # no mfa_code in this build

    bars = {}
    async with DXLinkStreamer(session) as streamer:
        logging.info("Subscribing to quotes for symbols: %s", SYMBOLS)
        await streamer.subscribe(Quote, SYMBOLS)

        async for quote in streamer.listen(Quote):
            if quote is None: 
                continue
            symbol = quote.event_symbol
            if symbol not in SYMBOLS:
                continue
            bid, ask = quote.bid_price, quote.ask_price
            if bid is None or ask is None:
                continue
            mid = float((bid + ask) / 2)
            now = datetime.now(timezone.utc)
            minute = floor_to_minute(now)
            key = (symbol, minute)
            bar = bars.get(key)
            if bar is None:
                bars[key] = bar = {"open": mid, "high": mid, "low": mid, "close": mid, "volume": 0.0}
            else:
                bar["high"] = max(bar["high"], mid)
                bar["low"] = min(bar["low"], mid)
                bar["close"] = mid

            # Flush completed minutes
            flush_keys = [k for k in bars.keys() if k[1] < minute]
            if not flush_keys:
                continue
            with conn.cursor() as cur:
                for fk in flush_keys:
                    fsym, fmin = fk
                    fbar = bars.pop(fk)
                    logging.info("Flushing %s %s O=%.4f H=%.4f L=%.4f C=%.4f V=%.0f",
                                 fmin.isoformat(), fsym,
                                 fbar["open"], fbar["high"], fbar["low"], fbar["close"], fbar["volume"])
                    cur.execute("""
                        INSERT INTO public.market_data_1m (ts, symbol, open, high, low, close, volume)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT DO NOTHING
                    """, (fmin, fsym, fbar["open"], fbar["high"], fbar["low"], fbar["close"], fbar["volume"]))

async def main():
    while True:
        try:
            await stream_once()
        except Exception as e:
            logging.exception("Streamer crashed, restarting in 10s: %s", e)
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
