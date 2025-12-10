CREATE TABLE public.live_quotes (
    symbol TEXT NOT NULL PRIMARY KEY,
    bid_price NUMERIC,
    bid_size BIGINT,
    ask_price NUMERIC,
    ask_size BIGINT,
    last_trade_price NUMERIC,
    last_trade_size BIGINT,
    last_update_ts TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_live_quotes_last_update_ts ON public.live_quotes(last_update_ts DESC);

ALTER TABLE public.live_quotes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access"
ON public.live_quotes
FOR SELECT
USING (true);
