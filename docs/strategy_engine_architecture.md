# Strategy Engine Architecture

This document outlines the architecture for the AgentTrader Strategy Engine, a service responsible for automatically evaluating market data and executing paper trades based on predefined strategies and risk limits.

## Overview

The Strategy Engine is a Python service designed to run periodically (e.g., once per minute). In each run, it:
1.  Fetches recent market data (bars, options flow) and current account state (positions, balances) from Supabase.
2.  Evaluates one or more active strategies against this data.
3.  Checks any resulting trade signals against pre-configured risk limits.
4.  If a signal is valid and passes risk checks, it executes a paper trade via the existing Alpaca order path.
5.  Logs all decisions, signals, and trade outcomes to dedicated Supabase tables for analysis and monitoring.

## Initial Scope (Phase 4)

The initial implementation focuses on a single, simple strategy and robust risk management for paper trading only.

-   **Strategy**: A "Naive Flow + Trend" strategy that combines a simple moving average trend with options flow sentiment to generate buy/sell signals.
-   **Risk Management**: A set of Supabase tables (`strategy_definitions`, `strategy_limits`, `strategy_state`) will be used to enforce risk limits before any trade is placed. This includes limits on daily trades, position size, and notional value.
-   **Execution**: The engine will reuse the existing `manual_paper_trade.py` logic to place orders, ensuring a consistent execution path.
-   **Logging**: All strategy decisions, whether they result in a trade or not, will be logged to `public.strategy_logs`.

## Non-Goals

-   **Live Money Trading**: This phase is strictly for paper trading.
-   **Tastytrade Integration**: The engine will initially only support the existing Alpaca paper trading connection.
-   **Complex Strategies**: The initial strategy is intentionally simple to provide a solid foundation for future, more complex strategies.

This document precedes the implementation of the Strategy Engine.
