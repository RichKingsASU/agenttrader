from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os

from ..scripts.insert_paper_order import insert_paper_order

router = APIRouter()

RISK_SERVICE_URL = os.getenv("RISK_SERVICE_URL", "http://127.0.0.1:8002")

class TradeRequest(BaseModel):
    user_id: str
    broker_account_id: str
    strategy_id: str
    symbol: str
    instrument_type: str
    side: str
    order_type: str
    time_in_force: str = "day"
    notional: float
    quantity: float = None
    
@router.post("/trades/execute", status_code=201)
def execute_trade(trade_request: TradeRequest):
    # Hardcoded risk check for now
    risk_check_payload = {
        "current_open_positions": 0,
        "current_trades_today": 0,
        "current_day_loss": 0,
        "current_day_drawdown": 0,
        "order": {
            "instrument_type": trade_request.instrument_type,
            "symbol": trade_request.symbol,
            "side": trade_request.side,
            "order_type": trade_request.order_type,
            "time_in_force": trade_request.time_in_force,
            "notional": trade_request.notional,
            "strategy_id": trade_request.strategy_id,
            "broker_account_id": trade_request.broker_account_id,
        },
    }

    try:
        response = requests.post(
            f"{RISK_SERVICE_URL}/risk/check", json=risk_check_payload
        )
        response.raise_for_status()
        risk_result = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Risk service request failed: {e}")

    if not risk_result.get("allowed"):
        raise HTTPException(status_code=400, detail=f"Trade not allowed by risk service: {risk_result.get('reason')}")

    logical_order = trade_request.dict()
    logical_order["risk_allowed"] = True
    logical_order["risk_scope"] = "strategy"
    logical_order["risk_reason"] = "Allowed by risk check"

    try:
        inserted_order = insert_paper_order(logical_order)
        return inserted_order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert paper order: {e}")

