import psycopg2
from datetime import date, datetime, timezone, timedelta
from uuid import UUID

def get_or_create_strategy_definition(conn, name: str) -> UUID:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.strategy_definitions WHERE name = %s", (name,))
        result = cur.fetchone()
        if result:
            return result[0]
        else:
            cur.execute("INSERT INTO public.strategy_definitions (name) VALUES (%s) RETURNING id", (name,))
            return cur.fetchone()[0]

def get_or_create_today_state(conn, strategy_id: UUID, today: date):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM public.strategy_state WHERE strategy_id = %s AND trading_date = %s", (strategy_id, today))
        if not cur.fetchone():
            cur.execute("INSERT INTO public.strategy_state (strategy_id, trading_date) VALUES (%s, %s)", (strategy_id, today))

def load_limits(conn, strategy_id: UUID):
    with conn.cursor() as cur:
        cur.execute("SELECT max_daily_trades, max_position_size, max_notional_per_trade, max_notional_per_day, max_open_positions, cool_down_minutes FROM public.strategy_limits WHERE strategy_id = %s", (strategy_id,))
        return cur.fetchone()

def can_place_trade(conn, strategy_id: UUID, today: date, proposed_notional: float) -> bool:
    limits = load_limits(conn, strategy_id)
    if not limits:
        return True # No limits set

    with conn.cursor() as cur:
        cur.execute("SELECT trades_placed, notional_traded, last_trade_at FROM public.strategy_state WHERE strategy_id = %s AND trading_date = %s", (strategy_id, today))
        state = cur.fetchone()
        if not state:
            return True

        trades_placed, notional_traded, last_trade_at = state
        max_daily_trades, _, max_notional_per_trade, max_notional_per_day, _, cool_down_minutes = limits

        if max_daily_trades and trades_placed >= max_daily_trades:
            return False
        if max_notional_per_day and (notional_traded + proposed_notional) > max_notional_per_day:
            return False
        if max_notional_per_trade and proposed_notional > max_notional_per_trade:
            return False
        if last_trade_at and cool_down_minutes and (datetime.now(timezone.utc) - last_trade_at) < timedelta(minutes=cool_down_minutes):
            return False

    return True

def record_trade(conn, strategy_id: UUID, today: date, notional: float):
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE public.strategy_state SET trades_placed = trades_placed + 1, notional_traded = notional_traded + %s, last_trade_at = %s, updated_at = %s WHERE strategy_id = %s AND trading_date = %s",
            (notional, datetime.now(timezone.utc), datetime.now(timezone.utc), strategy_id, today)
        )

def log_decision(conn, strategy_id: UUID, symbol: str, decision: str, reason: str, signal_payload: dict, did_trade: bool, paper_trade_id: UUID = None):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.strategy_logs (strategy_id, symbol, decision, reason, signal_payload, did_trade, paper_trade_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (strategy_id, symbol, decision, reason, json.dumps(signal_payload), did_trade, paper_trade_id)
        )
