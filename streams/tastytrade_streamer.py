# streams/tastytrade_streamer.py
import os
import asyncio
import json
from datetime import datetime, timezone

import httpx
import psycopg2
from psycopg2.extras import execute_values
import websockets

DATABASE_URL = os.environ["DATABASE_URL"]
TASTYTRADE_USERNAME = os.environ["TASTYTRADE_USERNAME"]
TASTYTRADE_PASSWORD = os.environ["TASTYTRADE_PASSWORD"]
TASTYTRADE_ENV = os.getenv("TASTYTRADE_ENV", "sandbox")

SYMBOLS = ["SPY", "IWM"]

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

async def get_quote_token():
    # Use tastytrade Open API to login & fetch api-quote-token per docs.:contentReference[oaicite:4]{index=4}
    base = "https://api.tastyworks.com" if TASTYTRADE_ENV == "prod" else "https://api.cert.tastyworks.com"
    async with httpx.AsyncClient() as client:
        # 1) login -> session token
        resp = await client.post(
            f"{base}/sessions",
            json={"login": TASTYTRADE_USERNAME, "password": TASTYTRADE_PASSWORD},
        )
        resp.raise_for_status()
        session_token = resp.json()["data"]["session-token"]

        # 2) get api-quote-token
        headers = {"Authorization": session_token}
        resp2 = await client.get(f"{base}/quote-streamer-tokens", headers=headers)
        resp2.raise_for_status()
        return resp2.json()["data"]["token"]

def insert_candle(conn, symbol, ts, open_, high_, low_, close_, volume_):
    with conn.cursor() as cur:
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
            (ts, symbol, open_, high_, low_, close_, volume_),
        )
    conn.commit()

async def stream_dxlink():
    conn = get_db_conn()
    quote_token = await get_quote_token()

    # DXLink host from docs; adjust to sandbox/production as needed.:contentReference[oaicite:5]{index=5}
    ws_url = "wss://streamer-ws.tastyworks.com"  # example; confirm from docs

    async with websockets.connect(ws_url) as ws:
        # Authenticate per DXLink spec (using quote_token)
        auth_msg = {
            "type": "login",
            "token": quote_token,
        }
        await ws.send(json.dumps(auth_msg))

        # Subscribe to candle events for symbols
        # You will adjust message format to match DXLink CandleEvents spec.
        sub_msg = {
            "type": "subscribe",
            "channels": [
                {
                    "name": "candle",
                    "symbols": SYMBOLS,
                    "interval": "1",  # 1-minute
                }
            ],
        }
        await ws.send(json.dumps(sub_msg))
        print(f"[Tastytrade] Subscribed to 1m candles for {SYMBOLS}")

        async for msg in ws:
            data = json.loads(msg)
            # TODO: Adjust this parsing to your actual DXLink payload
            if data.get("type") == "candle":
                sym = data["symbol"]
                ts = datetime.fromtimestamp(data["time"] / 1000.0, tz=timezone.utc)
                o = float(data["open"])
                h = float(data["high"])
                l = float(data["low"])
                c = float(data["close"])
                v = float(data.get("volume", 0))
                print(f"[Tastytrade] 1m candle {sym} @ {ts} close={c}")
                insert_candle(conn, sym, ts, o, h, l, c, v)

async def main():
    while True:
        try:
            await stream_dxlink()
        except Exception as e:
            print(f"[Tastytrade] Stream error: {e}, reconnecting in 10s...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())