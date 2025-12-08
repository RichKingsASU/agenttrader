from ..models import Bar, FlowEvent
from decimal import Decimal

def evaluate(bars: list[Bar], flow_events: list[FlowEvent]) -> dict:
    """
    A naive strategy that combines a simple moving average trend with options flow sentiment.
    """
    if not bars or len(bars) < 2:
        return {"action": "flat", "reason": "Not enough bar data"}

    # Simple Trend
    last_close = bars[0].close
    avg_close = sum(b.close for b in bars) / len(bars)
    trend_up = last_close > avg_close

    # Flow Bias
    call_buy_size = sum(f.size for f in flow_events if f.side == 'buy' and f.option_symbol.endswith('C'))
    put_buy_size = sum(f.size for f in flow_events if f.side == 'buy' and f.option_symbol.endswith('P'))
    flow_bias_positive = call_buy_size > put_buy_size

    signal_payload = {
        "last_close": float(last_close),
        "avg_close": float(avg_close),
        "trend_up": trend_up,
        "call_buy_size": call_buy_size,
        "put_buy_size": put_buy_size,
        "flow_bias_positive": flow_bias_positive
    }

    if trend_up and flow_bias_positive:
        return {
            "action": "buy",
            "symbol": bars[0].symbol,
            "size": 1,
            "reason": "Price is above SMA and call flow is dominant.",
            "signal_payload": signal_payload
        }
    else:
        return {
            "action": "flat",
            "reason": "No clear buy signal.",
            "signal_payload": signal_payload
        }
