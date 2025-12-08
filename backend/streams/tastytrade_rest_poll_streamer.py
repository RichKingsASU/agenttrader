import os, time, logging
from datetime import datetime, timezone

import requests
import psycopg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

DB = os.environ.get("DATABASE_URL")
SYMBOLS = [s.strip() for s in os.environ.get("TASTY_SYMBOLS", "SPY,IWM").split(",") if s.strip()]

if not DB:
    raise RuntimeError("DATABASE_URL is required")

def floor_min(dt: datetime) -> datetime:
    return dt.replace(second=0, microsecond=0)

def fetch_quote(symbol: str) -> float | None:
    # Public tastytrade quotes endpoint; if this ever returns 4xx/5xx,
    # the script will just skip that tick and keep going.
    url = f"https://api.tastyworks.com/quotes/{symbol}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            logging.warning("Quote HTTP %s for %s", r.status_code, symbol)
            return None
        js = r.json()
        # accept either camelCase or snake_case just in case
        bid = js.get("bidPrice") or js.get("bid_price")
        ask = js.get("askPrice") or js.get("ask_price")
        if bid is None or ask is None:
            return None
        return (float(bid) + float(ask)) / 2.0
    except Exception as e:
        logging.warning("Quote error %s: %s", symbol, e)
        return None

def main():
    conn = psycopg.connect(DB)
    conn.autocommit = True
    bars = {}  # (symbol, minute_ts_utc) -> {open, high, low, close, volume}

    logging.info("Polling quotes for: %s", SYMBOLS)
    last_min = None

    while True:
        now = datetime.now(timezone.utc)
        cur_min = floor_min(now)

        # minute rollover -> flush completed minute bars
        if last_min is not None and cur_min > last_min:
            with conn.cursor() as cur:
                for (sym, ts), bar in list(bars.items()):
                    if ts < cur_min:
                        logging.info("Flushing %s %s O=%.4f H=%.4f L=%.4f C=%.4f V=%.0f",
                                     ts.isoformat(), sym,
                                     bar["open"], bar["high"], bar["low"], bar["close"], bar["volume"])
                        cur.execute("""
                          INSERT INTO public.market_data_1m (ts, symbol, open, high, low, close, volume)
                          VALUES (%s,%s,%s,%s,%s,%s,%s)
                          ON CONFLICT DO NOTHING
                        """, (ts, sym, bar["open"], bar["high"], bar["low"], bar["close"], bar["volume"]))
                        bars.pop((sym, ts), None)

        last_min = cur_min

        # poll all symbols
        for sym in SYMBOLS:
            mid = fetch_quote(sym)
            if mid is None:
                continue
            key = (sym, cur_min)
            bar = bars.get(key)
            if bar is None:
                bars[key] = {"open": mid, "high": mid, "low": mid, "close": mid, "volume": 0.0}
            else:
                if mid > bar["high"]: bar["high"] = mid
                if mid < bar["low"]:  bar["low"]  = mid
                bar["close"] = mid

        time.sleep(2)  # adjust if you want faster/slower polls

if __name__ == "__main__":
    main()
