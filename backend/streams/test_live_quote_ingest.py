import os
import requests
import psycopg2
from datetime import datetime

DB_URL = os.environ["DATABASE_URL"]
KEY = os.environ["ALPACA_KEY_ID"]
SEC = os.environ["ALPACA_SECRET_KEY"]
SYMBOLS = os.environ.get("TASTY_SYMBOLS", "SPY,IWM,QQQ").split(",")

def fetch_latest_quote(sym: str):
    url = f"https://data.alpaca.markets/v2/stocks/{sym}/quotes/latest"
    r = requests.get(
        url,
        headers={
            "APCA-API-KEY-ID": KEY,
            "APCA-API-SECRET-KEY": SEC,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("quote")

def main():
    conn = psycopg2.connect(DB_URL, sslmode="require")
    cur = conn.cursor()

    for sym in SYMBOLS:
        quote = fetch_latest_quote(sym)
        if not quote:
            print(f"No quote for {sym}")
            continue

        # Alpaca fields: t, bp, bs, ap, as, etc.
        ts = datetime.fromisoformat(quote["t"].replace("Z", "+00:00"))
        bp = quote.get("bp")
        bs = quote.get("bs")
        ap = quote.get("ap")
        aS = quote.get("as")  # ask size
        # For last_trade_price/size we can piggy-back on bid fields,
        # or you can wire a proper last_trade endpoint later.
        last_price = bp
        last_size = bs

        cur.execute(
            """
            INSERT INTO public.live_quotes
              (symbol, bid_price, bid_size, ask_price, ask_size,
               last_trade_price, last_trade_size, last_update_ts)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE
              SET bid_price        = EXCLUDED.bid_price,
                  bid_size         = EXCLUDED.bid_size,
                  ask_price        = EXCLUDED.ask_price,
                  ask_size         = EXCLUDED.ask_size,
                  last_trade_price = EXCLUDED.last_trade_price,
                  last_trade_size  = EXCLUDED.last_trade_size,
                  last_update_ts   = EXCLUDED.last_update_ts;
            """,
            (sym, bp, bs, ap, aS, last_price, last_size, ts),
        )

        print(f"Upserted live quote for {sym} at {ts}")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
