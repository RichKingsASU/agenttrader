-- Seed strategy_definitions
INSERT INTO public.strategy_definitions (name, description)
VALUES ('naive_flow_trend', 'Simple MA + flow-imbalance strategy for SPY/IWM/QQQ')
ON CONFLICT (name) DO NOTHING;

-- Seed strategy_limits
INSERT INTO public.strategy_limits (strategy_id, max_daily_trades, max_position_size, max_notional_per_trade, max_notional_per_day, max_open_positions, cool_down_minutes)
SELECT
    id,
    5,
    1,
    10000,
    30000,
    1,
    5
FROM public.strategy_definitions
WHERE name = 'naive_flow_trend'
AND NOT EXISTS (
    SELECT 1 FROM public.strategy_limits WHERE strategy_id = (SELECT id FROM public.strategy_definitions WHERE name = 'naive_flow_trend')
);