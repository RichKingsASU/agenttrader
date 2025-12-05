import os
import psycopg
from datetime import datetime, timedelta

# Sample market data for SPY and IWM
market_data = [
    {
        "symbol": "SPY",
        "ts": datetime.now() - timedelta(minutes=5),
        "open": 450.00,
        "high": 450.50,
        "low": 449.50,
        "close": 450.25,
        "volume": 100000,
    },
    {
        "symbol": "SPY",
        "ts": datetime.now() - timedelta(minutes=4),
        "open": 450.25,
        "high": 451.00,
        "low": 450.00,
        "close": 450.75,
        "volume": 120000,
    },
    {
        "symbol": "IWM",
        "ts": datetime.now() - timedelta(minutes=5),
        "open": 200.00,
        "high": 200.50,
        "low": 199.50,
        "close": 200.25,
        "volume": 80000,
    },
    {
        "symbol": "IWM",
        "ts": datetime.now() - timedelta(minutes=4),
        "open": 200.25,
        "high": 201.00,
        "low": 200.00,
        "close": 200.75,
        "volume": 90000,
    },
]

def main():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is required")

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for data in market_data:
                cur.execute(
                    """
                    insert into public.market_data_1m (ts, symbol, open, high, low, close, volume)
                    values (%s, %s, %s, %s, %s, %s, %s)
                    on conflict (ts, symbol) do nothing
                    """,
                    (
                        data["ts"],
                        data["symbol"],
                        data["open"],
                        data["high"],
                        data["low"],
                        data["close"],
                        data["volume"],
                    ),
                )
            conn.commit()
    print("Market data ingested successfully")


if __name__ == "__main__":
    main()
