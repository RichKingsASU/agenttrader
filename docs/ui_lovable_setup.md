# Lovable UI Setup

To ensure the AgentTrader dashboard in Lovable UI can connect to Supabase, you must set the following environment variables in your Lovable deployment:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`

These variables are used by the `supabaseClient.ts` in the frontend to establish a connection to your Supabase project. Without these, the dashboard will not be able to fetch and display real-time market data or paper trade history.

Once configured, the dashboard will display:
- A "System Health" banner indicating the status of the ingestion loop and Alpaca paper trading authentication.
- A table with recent market data from `public.market_data_1m`.
- A table showing your recent paper trades from `public.paper_trades`.
