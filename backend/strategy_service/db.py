import os
import psycopg
import json
from contextlib import contextmanager
from psycopg.rows import dict_row

from .models import PaperOrderCreate, PaperOrder

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL env var is required for strategy_service")


@contextmanager
def get_conn():
    with psycopg.connect(DATABASE_URL) as conn:
        yield conn


def insert_paper_order(payload: PaperOrderCreate) -> PaperOrder:
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                insert into public.paper_orders (
                    user_id,
                    broker_account_id,
                    strategy_id,
                    symbol,
                    instrument_type,
                    side,
                    order_type,
                    time_in_force,
                    notional,
                    quantity,
                    risk_allowed,
                    risk_scope,
                    risk_reason,
                    raw_order,
                    status
                )
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                returning *
                """,
                (
                    str(payload.user_id),
                    str(payload.broker_account_id),
                    str(payload.strategy_id),
                    payload.symbol,
                    payload.instrument_type,
                    payload.side,
                    payload.order_type,
                    payload.time_in_force,
                    payload.notional,
                    payload.quantity,
                    payload.risk_allowed,
                    payload.risk_scope,
                    payload.risk_reason,
                    json.dumps(payload.raw_order),
                    payload.status,
                ),
            )
            row = cur.fetchone()
            conn.commit()

    if not row:
        return None

    return PaperOrder(**row)
