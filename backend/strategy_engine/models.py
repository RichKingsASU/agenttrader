from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Bar:
    symbol: str
    ts: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

@dataclass
class FlowEvent:
    symbol: str
    option_symbol: str
    side: str
    size: int
    notional: Decimal
    event_ts: datetime

@dataclass
class Position:
    symbol: str
    qty: Decimal
    avg_price: Decimal
    market_value: Decimal

# Helper functions to fetch data from Supabase
# These would use psycopg2 or asyncpg, matching the project's preference.
