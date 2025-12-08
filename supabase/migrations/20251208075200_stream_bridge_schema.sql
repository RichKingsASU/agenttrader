create table if not exists public.options_flow (
    id                uuid primary key default gen_random_uuid(),
    received_at       timestamptz not null default now(),
    event_ts          timestamptz not null,
    symbol            text not null,
    option_symbol     text not null,
    side              text not null check (side in ('buy', 'sell', 'unknown')),
    size              numeric not null,
    notional          numeric,
    strike            numeric,
    expiration        date,
    option_type       text check (option_type in ('call','put')),
    trade_price       numeric,
    bid               numeric,
    ask               numeric,
    venue             text,
    source            text not null default 'dev_console',
    raw               jsonb
);

create index if not exists idx_options_flow_symbol_ts
    on public.options_flow(symbol, event_ts desc);

create table if not exists public.news_events (
    id             uuid primary key default gen_random_uuid(),
    received_at    timestamptz not null default now(),
    event_ts       timestamptz,
    source         text not null,
    symbol         text,
    headline       text not null,
    body           text,
    url            text,
    category       text,
    sentiment      text,
    importance     integer,
    raw            jsonb,
    unique (source, event_ts, headline)
);

create index if not exists idx_news_symbol_ts
    on public.news_events(symbol, event_ts desc nulls last);

create table if not exists public.broker_accounts (
    id                  uuid primary key default gen_random_uuid(),
    broker              text not null,
    external_account_id text not null,
    label               text,
    created_at          timestamptz not null default now(),
    unique (broker, external_account_id)
);

create table if not exists public.broker_positions (
    id                 uuid primary key default gen_random_uuid(),
    broker_account_id  uuid not null references public.broker_accounts(id) on delete cascade,
    symbol             text not null,
    qty                numeric not null,
    avg_price          numeric,
    market_value       numeric,
    updated_at         timestamptz not null,
    raw                jsonb,
    unique (broker_account_id, symbol)
);

create table if not exists public.broker_balances (
    id                 uuid primary key default gen_random_uuid(),
    broker_account_id  uuid not null references public.broker_accounts(id) on delete cascade,
    cash               numeric,
    buying_power       numeric,
    maintenance_margin numeric,
    equity             numeric,
    updated_at         timestamptz not null,
    raw                jsonb,
    unique (broker_account_id)
);
