
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from scripts.insert_paper_order import insert_paper_order

router = APIRouter()


class PaperOrderRequest(BaseModel):
    user_id: str
    broker_account_id: str
    strategy_id: str
    symbol: str
    instrument_type: str
    side: str
    order_type: str
    time_in_force: str = "day"
    notional: float
    quantity: float | None = None


@router.post("/paper_orders", tags=["paper_orders"])
async def create_paper_order(order: PaperOrderRequest):
    # 1. Run risk check
    async with httpx.AsyncClient() as client:
        try:
            risk_check_payload = {
                "user_id": order.user_id,
                "broker_account_id": order.broker_account_id,
                "strategy_id": order.strategy_id,
                "symbol": order.symbol,
                "notional": str(order.notional),
                "side": order.side,
                "current_open_positions": 0,
                "current_trades_today": 0,
                "current_day_loss": "0.0",
                "current_day_drawdown": "0.0",
            }
            response = await client.post(
                "http://127.0.0.1:8002/risk/check-trade",
                json=risk_check_payload,
            )
            response.raise_for_status()
            risk_result = response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f"Error connecting to risk service: {e}"
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code, detail=f"Risk service error: {e.response.text}"
            )

    # 2. If allowed, insert paper order
    if risk_result.get("allowed"):
        logical_order = order.dict()
        logical_order["risk_allowed"] = True
        inserted = insert_paper_order(logical_order)
        return inserted
    else:
        # If risk check fails, return the reason
        raise HTTPException(status_code=400, detail=risk_result)

