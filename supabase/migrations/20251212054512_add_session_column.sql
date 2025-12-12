ALTER TABLE public.market_data_1m ADD COLUMN IF NOT EXISTS session TEXT;
ALTER TABLE public.live_quotes ADD COLUMN IF NOT EXISTS session TEXT;
