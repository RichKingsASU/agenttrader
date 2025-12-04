from fastapi import APIRouter
from uuid import UUID
from decimal import Decimal

from psycopg.rows import dict_row

from ..db import get_conn
from ..models import TradeCheckRequest, RiskCheckResult

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/limits")
def get_risk_limits(user_id: UUID, broker_account_id: UUID, strategy_id: UUID | None = None):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            if strategy_id:
                cur.execute(
                    """
                    select *
                    from public.risk_limits
                    where user_id = %s
                      and scope = 'strategy'
                      and broker_account_id = %s
                      and strategy_id = %s
                    """,
                    (str(user_id), str(broker_account_id), str(strategy_id)),
                )
            else:
                cur.execute(
                    """
                    select *
                    from public.risk_limits
                    where user_id = %s
                      and scope = 'account'
                      and broker_account_id = %s
                    """,
                    (str(user_id), str(broker_account_id)),
                )
            rows = cur.fetchall()

    return rows


@router.post("/check-trade", response_model=RiskCheckResult)
def check_trade(payload: TradeCheckRequest):
    with get_conn() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            strat_limits = None
            if payload.strategy_id:
                cur.execute(
                    """
                    select *
                    from public.risk_limits
                    where user_id = %s
                      and scope = 'strategy'
                      and broker_account_id = %s
                      and strategy_id = %s
                      and enabled = true
                    """,
                    (str(payload.user_id), str(payload.broker_account_id), str(payload.strategy_id)),
                )
                strat_limits = cur.fetchone()

            cur.execute(
                """
                select *
                from public.risk_limits
                where user_id = %s
                  and scope = 'account'
                  and broker_account_id = %s
                  and enabled = true
                """,
                (str(payload.user_id), str(payload.broker_account_id)),
            )
            acct_limits = cur.fetchone()

    def apply_limits(limits: dict, scope: str) -> RiskCheckResult | None:
        if not limits:
            return None

        max_notional_per_trade = limits.get("max_notional_per_trade")
        if max_notional_per_trade is not None and payload.notional > Decimal(max_notional_per_trade):
            return RiskCheckResult(
                allowed=False,
                reason=f"Notional {payload.notional} exceeds max_notional_per_trade {max_notional_per_trade}",
                scope=scope,
            )

        max_trades_per_day = limits.get("max_trades_per_day")
        if max_trades_per_day is not None and payload.current_trades_today + 1 > max_trades_per_day:
            return RiskCheckResult(
                allowed=False,
                reason=f"Trade count {payload.current_trades_today + 1} exceeds max_trades_per_day {max_trades_per_day}",
                scope=scope,
            )

        max_open_positions = limits.get("max_open_positions")
        if max_open_positions is not None and payload.current_open_positions + 1 > max_open_positions:
            return RiskCheckResult(
                allowed=False,
                reason=f"Open positions {payload.current_open_positions + 1} exceeds max_open_positions {max_open_positions}",
                scope=scope,
            )

        max_loss_per_day = limits.get("max_loss_per_day")
        if max_loss_per_day is not None and payload.current_day_loss < Decimal(0) and abs(payload.current_day_loss) >= Decimal(max_loss_per_day):
            return RiskCheckResult(
                allowed=False,
                reason=f"Current day loss {payload.current_day_loss} exceeds max_loss_per_day {max_loss_per_day}",
                scope=scope,
            )

        max_drawdown_per_day = limits.get("max_drawdown_per_day")
        if max_drawdown_per_day is not None and payload.current_day_drawdown > Decimal(max_drawdown_per_day):
            return RiskCheckResult(
                allowed=False,
                reason=f"Current day drawdown {payload.current_day_drawdown} exceeds max_drawdown_per_day {max_drawdown_per_day}",
                scope=scope,
            )

        return None

    if payload.strategy_id:
        result = apply_limits(strat_limits, "strategy")
        if result is not None:
            return result

    result = apply_limits(acct_limits, "account")
    if result is not None:
        return result

    return RiskCheckResult(allowed=True, reason=None, scope=None)
