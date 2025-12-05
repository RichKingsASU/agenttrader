from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
import requests
import json

from psycopg.rows import dict_row

from ..db import get_conn, insert_paper_order
from ..models import StrategyCreate, Strategy, PaperOrderCreate, PaperOrder

router = APIRouter(prefix="/strategies", tags=["strategies"])


def _row_to_strategy(row) -> Strategy:
    return Strategy(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        description=row["description"],
        status=row["status"],
        target_symbols=row["target_symbols"],
        instrument=row["instrument"],
        broker_account_id=row["broker_account_id"],
        config=row["config"],
        trading_session=row["trading_session"],
    )


@router.get("/", response_model=List[Strategy])
def list_strategies(user_id: UUID):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select *
                from public.strategies
                where user_id = %s
                order by created_at desc
                """,
                (str(user_id),),
            )
            rows = cur.fetchall()
    return [_row_to_strategy(row) for row in rows]


@router.post("/", response_model=Strategy)
def create_strategy(user_id: UUID, payload: StrategyCreate):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                insert into public.strategies (
                    user_id,
                    name,
                    description,
                    status,
                    target_symbols,
                    instrument,
                    broker_account_id,
                    config,
                    trading_session
                )
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                returning *
                """,
                (
                    str(user_id),
                    payload.name,
                    payload.description,
                    payload.status,
                    payload.target_symbols,
                    payload.instrument,
                    str(payload.broker_account_id),
                    payload.config,
                    payload.trading_session,
                ),
            )
            row = cur.fetchone()
            conn.commit()

    if not row:
        raise HTTPException(status_code=500, detail="Failed to create strategy")

    return _row_to_strategy(row)


@router.post("/simulate-order", response_model=PaperOrder)
def simulate_order(payload: PaperOrderCreate):
    # For now, we'll assume a simple risk check that always passes.
    # In the future, we can add a more sophisticated risk check here.
    risk_check_payload = {
        "user_id": str(payload.user_id),
        "strategy_id": str(payload.strategy_id),
        "broker_account_id": str(payload.broker_account_id),
        "symbol": payload.symbol,
        "notional": payload.notional,
        "current_open_positions": 0,
        "current_trades_today": 0,
        "current_day_loss": 0,
    }
    
    try:
        response = requests.post("http://127.0.0.1:8002/risk-check", json=risk_check_payload)
        response.raise_for_status()
        risk_result = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to risk service: {e}")


    if not risk_result.get("allowed"):
        raise HTTPException(status_code=400, detail=f"Risk check failed: {risk_result.get('reason')}")

    paper_order = insert_paper_order(payload)
    if not paper_order:
        raise HTTPException(status_code=500, detail="Failed to create paper order")

    return paper_order
