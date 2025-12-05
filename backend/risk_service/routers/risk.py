from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class Order(BaseModel):
    instrument_type: str
    symbol: str
    side: str
    order_type: str
    time_in_force: str
    notional: float
    strategy_id: str
    broker_account_id: str

class RiskCheckRequest(BaseModel):
    current_open_positions: int
    current_trades_today: int
    current_day_loss: float
    current_day_drawdown: float
    order: Order

@router.post("/risk/check")
def check_risk(request: RiskCheckRequest):
    # For now, we will always allow the trade.
    # This is a placeholder for the actual risk check logic.
    return {"allowed": True, "reason": "Risk check not implemented yet."}
