import os, time, logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import requests
import psycopg2
from psycopg2.extras import execute_values
from tenacity import retry, wait_exponential, stop_after_attempt

DB_URL = os.environ["DATABASE_URL"]
SYMBOLS = [s.strip() for s in os.environ.get("TASTY_SYMBOLS", "SPY,IWM").split(",") if s.strip()]

ALPACA_HOST = os.environ.get("ALPACA_DATA_HOST", "https://data.alpaca.markets")
ALPACA_KEY  = os.environ.get("ALPACA_KEY_ID")
ALPACA_SEC  = os.environ.get("ALPACA_SECRET_KEY")

session = requests.Session()
if ALPACA_KEY and ALPACA_SEC:
    session.headers.update({
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SEC,
    })

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def fetch_quote(sym: str) -> Optional[Dict[str, Any]]:
    """
    Fetch the latest 1-minute bar for `sym` from Alpaca Market Data v2.
    Returns a dict with open/high/low/close/volume if available.
    """
    if not (ALPACA_KEY and ALPACA_SEC):
        logging.warning("ALPACA credentials not set — skipping fetch for %s", sym)
        return None
    try:
        # latest bar endpoint
        url = f"{ALPACA_HOST}/v2/stocks/{sym}/bars?timeframe=1Min&limit=1"
        r = session.get(url, timeout=10)
        if r.status_code != 200:
            logging.warning("Alpaca bars HTTP %s for %s: %s", r.status_code, sym, r.text[:200])
            return None
        data = r.json()
        bars = data.get("bars") or []
        if not bars:
            return None
        bar = bars[0]
        # Alpaca bar fields: t (ISO), o, h, l, c, v
        return {
            "open":  bar.get("o"),
            "high":  bar.get("h"),
            "low":   bar.get("l"),
            "close": bar.get("c"),
            "volume":bar.get("v"),
            "ts":    bar.get("t"),
        }
    except Exception as e:
        logging.exception("fetch_quote failed for %s: %s", sym, e)
        return None

def to_minute_ts(dt: datetime):
    return dt.replace(second=0, microsecond=0)

def parse_ts(payload_ts: Optional[str]) -> datetime:
    # If Alpaca gives ISO8601 with Z, parse conservatively; else fall back to now
    if not payload_ts:
        return datetime.now(timezone.utc)
    try:
        # Example: "2025-12-05T03:35:00Z"
        from datetime import datetime
        if payload_ts.endswith("Z"):
            payload_ts = payload_ts[:-1] + "+00:00"
        return datetime.fromisoformat(payload_ts).astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)

def map_payload_to_ohlcv(sym: str, payload: Dict[str, Any], ts_minute: datetime):
    # prefer bar timestamp if available to keep bars aligned
    ts = parse_ts(payload.get("ts")) if payload.get("ts") else ts_minute

    def _f(key, default=None):
        v = payload.get(key, default)
        try:
            return float(v) if v is not None else None
        except Exception:
            return None

    opn  = _f("open")
    high = _f("high", opn)
    low  = _f("low", opn)
    cls  = _f("close", opn)
    vol  = payload.get("volume") or 0
    try:
        vol = int(vol)
    except Exception:
        vol = 0

    if cls is None:
        return None
    if high is None: high = cls
    if low  is None: low  = cls
    if opn  is None: opn  = cls

    return (sym, ts, opn, high, low, cls, vol)

def upsert_minute_bars(rows):
    if not rows:
        return
    try:
        with psycopg2.connect(DB_URL) as conn, conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO public.market_data_1m (symbol, ts, open, high, low, close, volume)
                VALUES %s
                ON CONFLICT (symbol, ts) DO UPDATE
                SET open=EXCLUDED.open,
                    high=EXCLUDED.high,
                    low=EXCLUDED.low,
                    close=EXCLUDED.close,
                    volume=EXCLUDED.volume
            """, rows)
    except psycopg2.Error as e:
        logging.error("Database error during upsert: %s", e)
    except Exception as e:
        logging.error("An unexpected error occurred during upsert: %s", e)

def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("Starting REST quotes runner for symbols: %s", ",".join(SYMBOLS))
    while True:
        # we’ll use bar timestamp if present; ts_minute is a fallback
        ts_minute = to_minute_ts(datetime.now(timezone.utc))
        batch = []
        for sym in SYMBOLS:
            data = fetch_quote(sym)
            if not data:
                logging.warning("No data for %s (check ALPACA creds or symbol).", sym)
                continue
            mapped = map_payload_to_ohlcv(sym, data, ts_minute)
            if mapped:
                batch.append(mapped)
        if batch:
            upsert_minute_bars(batch)
            logging.info("Upserted %d row(s)", len(batch))
        time.sleep(5)  # poll every 5s; adjust as you like
if __name__ == "__main__":
    run()
