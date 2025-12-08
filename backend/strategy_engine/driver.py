import os
import sys
import subprocess
import psycopg2
from datetime import date, datetime, timezone
from decimal import Decimal
from .config import load_config
from . import risk
from .strategies import naive_flow_trend

def get_recent_bars(conn, symbol, lookback_minutes):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT symbol, ts, open, high, low, close, volume FROM public.market_data_1m WHERE symbol = %s AND ts > %s ORDER BY ts DESC",
            (symbol, datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes))
        )
        return [Bar(*row) for row in cur.fetchall()]

def get_recent_flow(conn, symbol, lookback_minutes):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT symbol, option_symbol, side, size, notional, event_ts FROM public.options_flow WHERE symbol = %s AND event_ts > %s ORDER BY event_ts DESC",
            (symbol, datetime.now(timezone.utc) - timedelta(minutes=lookback_minutes))
        )
        return [FlowEvent(*row) for row in cur.fetchall()]

def main(execute: bool):
    cfg = load_config()
    today = date.today()

    with psycopg2.connect(cfg.database_url) as conn:
        strategy_id = risk.get_or_create_strategy_definition(conn, cfg.strategy_name)
        risk.get_or_create_today_state(conn, strategy_id, today)

        for symbol in cfg.strategy_symbols:
            bars = get_recent_bars(conn, symbol, cfg.strategy_bar_lookback_minutes)
            flow = get_recent_flow(conn, symbol, cfg.strategy_flow_lookback_minutes)
            decision = naive_flow_trend.evaluate(bars, flow)

            if decision['action'] != 'flat' and execute:
                proposed_notional = float(bars[0].close) * decision['size']
                if risk.can_place_trade(conn, strategy_id, today, proposed_notional):
                    try:
                        subprocess.run(
                            ["python", "backend/streams/manual_paper_trade.py", symbol, decision['action'], str(decision['size'])],
                            check=True, capture_output=True, text=True
                        )
                        # TODO: This is a simplification. The `manual_paper_trade.py` script would need to be modified to return the trade ID.
                        risk.record_trade(conn, strategy_id, today, proposed_notional)
                        risk.log_decision(conn, strategy_id, symbol, decision['action'], decision['reason'], decision['signal_payload'], True)
                    except subprocess.CalledProcessError as e:
                        risk.log_decision(conn, strategy_id, symbol, decision['action'], f"Failed to place trade: {e.stderr}", decision['signal_payload'], False)
                else:
                    risk.log_decision(conn, strategy_id, symbol, decision['action'], "Risk limits exceeded", decision['signal_payload'], False)
            else:
                risk.log_decision(conn, strategy_id, symbol, decision['action'], decision['reason'], decision['signal_payload'], False)

if __name__ == "__main__":
    execute = "--execute" in sys.argv
    main(execute)
