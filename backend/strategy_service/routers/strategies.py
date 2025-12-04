from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID

from psycopg.rows import dict_row

from ..db import get_conn
from ..models import StrategyCreate, Strategy

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
