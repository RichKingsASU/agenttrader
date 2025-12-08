from dataclasses import dataclass
import os

@dataclass
class Config:
    database_url: str
    strategy_name: str
    strategy_symbols: list[str]
    strategy_bar_lookback_minutes: int
    strategy_flow_lookback_minutes: int

def load_config() -> Config:
    return Config(
        database_url=os.environ["DATABASE_URL"],
        strategy_name=os.environ.get("STRATEGY_NAME", "naive_flow_trend"),
        strategy_symbols=os.environ.get("STRATEGY_SYMBOLS", "SPY,IWM").split(","),
        strategy_bar_lookback_minutes=int(os.environ.get("STRATEGY_BAR_LOOKBACK_MINUTES", "30")),
        strategy_flow_lookback_minutes=int(os.environ.get("STRATEGY_FLOW_LOOKBACK_MINUTES", "5")),
    )
