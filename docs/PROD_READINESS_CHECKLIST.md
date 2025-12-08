# Production Readiness Checklist

This document tracks the major milestones for getting AgentTrader ready for production.

## Core Backend & Ingestion
- [x] Harden Alpaca ingestion scripts (`alpaca_backfill_bars.py`, `quotes_rest_runner.py`)
- [x] Harden Alpaca ingestion loop (`run-alpaca-minute-loop.sh`) with PID lock
- [x] Verify Alpaca paper trading credentials and order path
- [x] Implement `paper_trades` table in Supabase
- [x] Implement `manual_paper_trade.py` script

## Stream Bridge
- [x] Design and document Stream Bridge architecture
- [x] Create Supabase schema for `options_flow`, `news_events`, `broker_accounts`, `broker_positions`, `broker_balances`
- [x] Implement `SupabaseWriter` for Stream Bridge
- [x] Implement `NewsStreamClient` scaffold
- [x] Implement `OptionsFlowClient` scaffold
- [x] Implement `AccountUpdatesClient` scaffold
- [x] Add deployment scaffolding for Stream Bridge

## Frontend
- [x] Scaffold basic Next.js frontend
- [x] Add `MarketDataWidget` and `PaperTradesWidget`
- [x] Add `NewsEventsWidget`
- [x] Add `OptionsFlowWidget`
- [x] Add `BrokerPositionsWidget`

## Deployment & Operations
- [x] Create Cloud Run Job and Scheduler helper scripts for Alpaca ingestion
- [ ] Finalize Cloud Run / Scheduler setup for Alpaca ingestion
- [ ] Deploy Stream Bridge service
- [ ] Deploy frontend to Vercel/Lovable
- [ ] Configure production environment variables (Supabase, Alpaca, Developer Console)

## Strategy & Risk
- [x] Create naive strategy driver skeleton
- [ ] Implement robust strategy engine
- [ ] Implement risk management service
- [ ] Implement position and P&L tracking
