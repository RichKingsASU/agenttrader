create table public.market_data_1m (
    ts timestamptz not null,
    symbol text not null,
    open double precision not null,
    high double precision not null,
    low double precision not null,
    close double precision not null,
    volume bigint not null,

    primary key (ts, symbol)
);

-- efficiently query by symbol and time
create index on public.market_data_1m (symbol, ts desc);

-- enable timescaledb extension if you have it
-- select create_hypertable('market_data_1m', 'ts');
