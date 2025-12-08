
CREATE TABLE IF NOT EXISTS public.strategy_definitions (
    id uuid primary key default gen_random_uuid(),
    name text not null unique,
    description text,
    is_active boolean not null default true,
    created_at timestamptz default now()
);

CREATE TABLE IF NOT EXISTS public.strategy_limits (
    id uuid primary key default gen_random_uuid(),
    strategy_id uuid references public.strategy_definitions(id) on delete cascade,
    max_daily_trades integer,
    max_position_size numeric,
    max_notional_per_trade numeric,
    max_notional_per_day numeric,
    max_open_positions integer,
    cool_down_minutes integer default 0,
    created_at timestamptz default now()
);

CREATE TABLE IF NOT EXISTS public.strategy_state (
    id uuid primary key default gen_random_uuid(),
    strategy_id uuid references public.strategy_definitions(id) on delete cascade,
    trading_date date not null,
    trades_placed integer not null default 0,
    notional_traded numeric not null default 0,
    last_signal_at timestamptz,
    last_trade_at timestamptz,
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    unique (strategy_id, trading_date)
);

CREATE TABLE IF NOT EXISTS public.strategy_logs (
    id uuid primary key default gen_random_uuid(),
    created_at timestamptz default now(),
    strategy_id uuid references public.strategy_definitions(id) on delete set null,
    symbol text,
    decision text,
    reason text,
    signal_payload jsonb,
    did_trade boolean,
    paper_trade_id uuid references public.paper_trades(id) on delete set null
);

CREATE INDEX IF NOT EXISTS idx_strategy_state_strategy_id_trading_date ON public.strategy_state (strategy_id, trading_date);
CREATE INDEX IF NOT EXISTS idx_strategy_logs_strategy_id_created_at ON public.strategy_logs (strategy_id, created_at);
