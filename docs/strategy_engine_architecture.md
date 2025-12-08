# AgentTrader - Strategy Engine Architecture

## Strategy Engine – Phase 4 (2025-12-08)

### Role of Strategy Engine

The Strategy Engine is a core component of the AgentTrader system responsible for making autonomous trading decisions. It operates by analyzing market data and other signals, applying a defined trading strategy, and generating trade signals. These signals are then passed to the execution component, which places orders with the broker.

### Inputs

The Strategy Engine consumes the following data inputs:

- **Market Data:** 1-minute bar data (`public.market_data_1m`) for SPY, IWM, and QQQ.
- **Options Flow:** Real-time options flow data (`public.options_flow`) to gauge market sentiment.
- **Broker Positions:** Account position and balance data (`public.broker_positions`, `public.broker_balances`) for position management and risk control.

### Outputs

The Strategy Engine produces the following outputs:

- **Paper Trades:** Trade orders are sent to the Alpaca paper trading environment and recorded in the `public.paper_trades` table.
- **Strategy Logs:** Detailed logs of every decision made by the strategy, including the reason and the data that led to the decision. These logs are stored in the `public.strategy_logs` table.

### Initial Scope

The initial version of the Strategy Engine will implement a simple "Naive Flow + Trend" strategy. This strategy is designed to be a baseline for future, more complex strategies. The key characteristics of the initial scope are:

- **Paper Trading Only:** All trades will be executed in the Alpaca paper trading environment. No real capital will be at risk.
- **Risk-Limited:** The strategy will be subject to basic risk controls, including limits on the number of daily trades, position size, and notional value per trade.
- **Naive Flow + Trend Strategy:** The strategy will make decisions based on a combination of simple trend-following and options flow analysis.