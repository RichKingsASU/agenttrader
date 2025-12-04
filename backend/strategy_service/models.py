from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID


class StrategyCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "draft"
    target_symbols: List[str] = ["SPY", "IWM"]
    instrument: str = "option"
    broker_account_id: UUID
    config: dict = {}
    trading_session: dict = {
        "timezone": "America/New_York",
        "market_hours_only": True,
        "session_start": "09:30",
        "session_end": "16:00",
    }


class Strategy(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    status: str
    target_symbols: List[str]
    instrument: str
    broker_account_id: UUID
    config: dict
    trading_session: dict
