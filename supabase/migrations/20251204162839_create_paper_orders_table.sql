-- Create paper_orders table
create table public.paper_orders (
  id uuid primary key default gen_random_uuid(),

  user_id uuid not null,
  broker_account_id uuid not null,
  strategy_id uuid not null,

  symbol text not null,
  instrument_type text not null,
  side text not null,
  order_type text not null,
  time_in_force text not null default 'day',

  notional numeric(18,2) not null,
  quantity numeric(18,8),

  risk_allowed boolean not null default true,
  risk_scope text,
  risk_reason text,

  raw_order jsonb not null,

  status text not null default 'simulated',
  created_at timestamptz not null default now()
);

alter table public.paper_orders
  add constraint fk_paper_orders_broker_accounts
    foreign key (broker_account_id)
    references public.broker_accounts(id)
    on delete cascade;

alter table public.paper_orders
  add constraint fk_paper_orders_strategies
    foreign key (strategy_id)
    references public.strategies(id)
    on delete cascade;
