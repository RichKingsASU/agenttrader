import os

class Config:
    DATABASE_URL = os.environ.get('DATABASE_URL')
    STRATEGY_NAME = os.environ.get('STRATEGY_NAME', 'naive_flow_trend')
    STRATEGY_SYMBOLS = os.environ.get('STRATEGY_SYMBOLS', 'SPY,IWM,QQQ').split(',')
    STRATEGY_BAR_LOOKBACK_MINUTES = int(os.environ.get('STRATEGY_BAR_LOOKBACK_MINUTES', 30))
    STRATEGY_FLOW_LOOKBACK_MINUTES = int(os.environ.get('STRATEGY_FLOW_LOOKBACK_MINUTES', 5))

config = Config()