import os, requests, psycopg2, datetime as dt
import logging
from psycopg2.extras import execute_values
from tenacity import retry, wait_exponential, stop_after_attempt

# --- Standard Header ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_URL = os.environ["DATABASE_URL"]
KEY = os.environ["ALPACA_KEY_ID"]
SEC = os.environ["ALPACA_SECRET_KEY"]
SYMS = os.environ.get("TASTY_SYMBOLS", "SPY,IWM,QQQ").split(",")
FEED = os.environ.get("ALPACA_FEED", "iex")
BASE = "https://data.alpaca.markets/v2/stocks"
HDRS = {"APCA-API-KEY-ID": KEY, "APCA-API-SECRET-KEY": SEC}
# --- End Standard Header ---

@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(5))
def fetch_bars(sym, limit=100):
    """Fetches the last N bars for a symbol."""
    url = f"{BASE}/{sym}/bars"
    try:
        r = requests.get(url, headers=HDRS, params={"timeframe":"1Min", "limit":limit, "feed":FEED, "adjustment":"all"})
        r.raise_for_status()
        return r.json().get("bars", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching bars for {sym}: {e}")
        raise

def upsert_bars(conn, sym, bars):
    """Upserts a list of bars for a given symbol into the database."""
    if not bars:
        return 0
    rows = []
    for b in bars:
        try:
            ts = dt.datetime.fromisoformat(b["t"].replace("Z", "+00:00"))
            rows.append((sym, ts, b["o"], b["h"], b["l"], b["c"], b["v"]))
        except (TypeError, ValueError) as e:
            logger.warning(f"Skipping malformed bar for {sym} at ts {b.get('t')}: {e}")
            continue
    
    if not rows:
        return 0

    try:
        with conn.cursor() as cur:
            execute_values(cur, """
                INSERT INTO public.market_data_1m (symbol, ts, open, high, low, close, volume)
                VALUES %s
                ON CONFLICT (symbol, ts) DO UPDATE
                  SET open=EXCLUDED.open, high=EXCLUDED.high, low=EXCLUDED.low,
                      close=EXCLUDED.close, volume=EXCLUDED.volume;
            """, rows)
        conn.commit()
        return len(rows)
    except psycopg2.Error as e:
        logger.error(f"Database error during upsert for {sym}: {e}")
        conn.rollback()
        return 0

def main():
    """Main function to fetch and upsert bars for all symbols."""
    logger.info("Starting short-window ingest for symbols: %s", ", ".join(SYMS))
    total_upserted = 0
    try:
        with psycopg2.connect(DB_URL) as conn:
            for s in SYMS:
                bars = fetch_bars(s)
                upserted_count = upsert_bars(conn, s, bars)
                logger.info(f"{s}: upserted {upserted_count} bars")
                total_upserted += upserted_count
    except psycopg2.Error as e:
        logger.critical(f"Database connection failed: {e}")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}")
    finally:
        logger.info(f"Short-window ingest finished. Total bars upserted: {total_upserted}")

if __name__ == "__main__":
    main()