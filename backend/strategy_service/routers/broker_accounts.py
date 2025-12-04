from fastapi import APIRouter
from typing import List
from uuid import UUID

from psycopg.rows import dict_row

from ..db import get_conn

router = APIRouter(prefix="/broker-accounts", tags=["broker-accounts"])


@router.get("/", response_model=List[dict])
def list_broker_accounts(user_id: UUID):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                select id,
                       user_id,
                       broker_name,
                       account_label,
                       broker_account_id,
                       is_paper_trading,
                       created_at
                from public.broker_accounts
                where user_id = %s
                order by created_at desc
                """,
                (str(user_id),),
            )
            rows = cur.fetchall()
    return rows
