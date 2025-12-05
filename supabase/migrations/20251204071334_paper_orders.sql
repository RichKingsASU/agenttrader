-- Create paper_orders table for simulated (paper) executions
create table if not exists public.paper_orders (
  id uuid primary key default gen_random_uuid(),

  -- who owns this order
  user_id uuid not null,
  broker_account_id uuid not null,
  strategy_id uuid not null,

  -- order description
  symbol text not null,
  instrument_type text not null,     -- 'stock', 'option', 'future', etc.
  side text not null,                -- 'buy' | 'sell'
  order_type text not null,          -- 'market', 'limit', etc.
  time_in_force text not null default 'day',

  -- sizing
  notional numeric(18,2) not null,
  quantity numeric(18,8),

  -- risk info
  risk_allowed boolean not null default true,
  risk_scope text,                   -- 'account', 'strategy', etc.
  risk_reason text,                  -- why risk blocked it (if at all)

  -- full broker-style payload that would be sent to tastytrade later
  raw_order jsonb not null,

  -- lifecycle
  status text not null default 'simulated',   -- 'simulated', 'sent', 'filled', etc.
  created_at timestamptz not null default now()
);

-- Optional foreign keys (safe because these tables exist already)
alter table public.paper_orders
  add constraint paper_orders_broker_fk
    foreign key (broker_account_id)
    references public.broker_accounts(id)
    on delete cascade;

alter table public.paper_orders
  add constraint paper_orders_strategy_fk
    foreign key (strategy_id)
    references public.strategies(id)
    on delete cascade;
