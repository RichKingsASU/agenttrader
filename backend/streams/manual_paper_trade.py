import os
import sys
import json
import requests
import psycopg2
from decimal import Decimal

# --- Constants and Config ---
ALPACA_BASE = "https://paper-api.alpaca.markets/v2"
try:
    KEY = os.environ["ALPACA_KEY_ID"]
    SEC = os.environ["ALPACA_SECRET_KEY"]
    DB_URL = os.environ["DATABASE_URL"]
except KeyError as e:
    print(f"Error: Missing environment variable {e}")
    sys.exit(1)

HEADERS = {
    "APCA-API-KEY-ID": KEY,
    "APCA-API-SECRET-KEY": SEC,
    "Content-Type": "application/json",
}

def place_order(symbol: str, side: str, qty: int):
    """Places a market paper order with Alpaca."""
    print(f"Placing {side} order for {qty} {symbol}...")
    payload = {
        "symbol": symbol,
        "qty": str(qty),
        "side": side,
        "type": "market",
        "time_in_force": "day",
    }
    try:
        r = requests.post(f"{ALPACA_BASE}/orders", headers=HEADERS, json=payload)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error placing Alpaca order: {e}")
        if e.response:
            print(f"Alpaca response: {e.response.text}")
        return None

def record_trade(order_json):
    """Records the trade details into the Supabase paper_trades table."""
    if not order_json:
        print("Skipping trade recording due to failed order.")
        return

    print("Recording trade to Supabase...")
    symbol = order_json.get("symbol")
    side = order_json.get("side")
    qty = Decimal(order_json.get("qty", "0"))
    alpaca_order_id = order_json.get("id")
    status = order_json.get("status", "new")
    price = Decimal(order_json.get("filled_avg_price") or order_json.get("limit_price") or "0")

    try:
        with psycopg2.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public.paper_trades (symbol, side, qty, price, alpaca_order_id, status, source)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (symbol, side, qty, price, alpaca_order_id, status, 'manual_script')
                )
        print(f"Successfully recorded trade {alpaca_order_id} for {symbol}.")
    except psycopg2.Error as e:
        print(f"Database error during trade recording: {e}")

def main():
    """Main function to parse CLI args and execute a paper trade."""
    if len(sys.argv) != 4:
        print("Usage: python backend/streams/manual_paper_trade.py <SYMBOL> <buy|sell> <QTY>")
        sys.exit(1)

    symbol = sys.argv[1].upper()
    side = sys.argv[2].lower()
    try:
        qty = int(sys.argv[3])
        if qty <= 0:
            raise ValueError()
    except ValueError:
        print("Error: QTY must be a positive integer.")
        sys.exit(1)

    if side not in ['buy', 'sell']:
        print("Error: side must be 'buy' or 'sell'.")
        sys.exit(1)

    order_response = place_order(symbol, side, qty)
    
    if order_response:
        print(f"Alpaca order submitted: ID={order_response.get('id')}, Status={order_response.get('status')}")
        record_trade(order_response)

if __name__ == "__main__":
    main()
