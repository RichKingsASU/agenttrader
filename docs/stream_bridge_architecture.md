# Stream Bridge Architecture

This document outlines the architecture for the "Stream Bridge" microservice, which is responsible for ingesting real-time data streams from the Developer Console into the AgentTrader Supabase database.

## Overview

The Stream Bridge is a Python/asyncio microservice that subscribes to multiple external WebSocket streams for market data and account information. It normalizes the data from these streams and writes it to a set of dedicated tables in the Supabase database.

The primary data sources are assumed to be from the Developer Console, which may include streams from Polygon, OPRA, Benzinga, and TD Ameritrade. The exact WebSocket URLs and authentication details are to be provided later as environment variables.

## New Tables

The following new tables will be created in the `public` schema to support the Stream Bridge:

### `options_flow`

Stores high-volume options trading activity.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | Primary Key, Default: `gen_random_uuid()` | Unique identifier for each event. |
| `received_at` | `timestamptz`| Not Null, Default: `now()` | Timestamp when the event was received by the bridge. |
| `event_ts` | `timestamptz`| Not Null | The original timestamp of the event from the source. |
| `symbol` | `text` | Not Null | The underlying stock symbol. |
| `option_symbol`| `text` | Not Null | The full option symbol. |
| `side` | `text` | Not Null, Check: `in ('buy', 'sell', 'unknown')` | The side of the trade. |
| `size` | `numeric` | Not Null | The number of contracts traded. |
| `notional` | `numeric` | | The total value of the trade. |
| `strike` | `numeric` | | The strike price of the option. |
| `expiration` | `date` | | The expiration date of the option. |
| `option_type` | `text` | Check: `in ('call', 'put')` | The type of option. |
| `trade_price` | `numeric` | | The price at which the trade occurred. |
| `bid` | `numeric` | | The bid price at the time of the trade. |
| `ask` | `numeric` | | The ask price at the time of the trade. |
| `venue` | `text` | | The exchange or venue where the trade occurred. |
| `source` | `text` | Not Null, Default: `'dev_console'` | The source of the data. |
| `raw` | `jsonb` | | The raw, unprocessed event data. |

**Indexes:**
- `idx_options_flow_symbol_ts` on `(symbol, event_ts desc)`

### `news_events`

Stores news headlines and articles.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | Primary Key, Default: `gen_random_uuid()` | Unique identifier for each event. |
| `received_at` | `timestamptz`| Not Null, Default: `now()` | Timestamp when the event was received by the bridge. |
| `event_ts` | `timestamptz`| | The original timestamp of the event from the source. |
| `source` | `text` | Not Null | The source of the news (e.g., Benzinga). |
| `symbol` | `text` | | The stock symbol(s) associated with the news. |
| `headline` | `text` | Not Null | The news headline. |
| `body` | `text` | | The body of the news article. |
| `url` | `text` | | A URL to the full article. |
| `category` | `text` | | The category of the news. |
| `sentiment` | `text` | | The sentiment of the news (e.g., bullish, bearish). |
| `importance` | `integer` | | The importance of the news (e.g., 1-5). |
| `raw` | `jsonb` | | The raw, unprocessed event data. |

**Constraints:**
- Unique constraint on `(source, event_ts, headline)`

**Indexes:**
- `idx_news_symbol_ts` on `(symbol, event_ts desc nulls last)`

### `broker_accounts`

Stores information about connected brokerage accounts.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | Primary Key, Default: `gen_random_uuid()` | Unique identifier for each account. |
| `broker` | `text` | Not Null | The name of the brokerage (e.g., 'tastytrade', 'tradier'). |
| `external_account_id`| `text` | Not Null | The account ID from the brokerage. |
| `label` | `text` | | A user-defined label for the account. |
| `created_at` | `timestamptz`| Not Null, Default: `now()` | Timestamp when the account was added. |

**Constraints:**
- Unique constraint on `(broker, external_account_id)`

### `broker_positions`

Stores the positions for each brokerage account.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | Primary Key, Default: `gen_random_uuid()` | Unique identifier for each position. |
| `broker_account_id` | `uuid` | Not Null, Foreign Key to `broker_accounts(id)` | The brokerage account this position belongs to. |
| `symbol` | `text` | Not Null | The stock or option symbol. |
| `qty` | `numeric` | Not Null | The quantity of the position. |
| `avg_price` | `numeric` | | The average price of the position. |
| `market_value` | `numeric` | | The current market value of the position. |
| `updated_at` | `timestamptz`| Not Null | The last time this position was updated. |
| `raw` | `jsonb` | | The raw, unprocessed position data. |

**Constraints:**
- Unique constraint on `(broker_account_id, symbol)`

### `broker_balances`

Stores the balances for each brokerage account.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `uuid` | Primary Key, Default: `gen_random_uuid()` | Unique identifier for each balance record. |
| `broker_account_id` | `uuid` | Not Null, Foreign Key to `broker_accounts(id)` | The brokerage account this balance belongs to. |
| `cash` | `numeric` | | The cash balance. |
| `buying_power` | `numeric` | | The buying power. |
| `maintenance_margin`| `numeric` | | The maintenance margin. |
| `equity` | `numeric` | | The total equity. |
| `updated_at` | `timestamptz`| Not Null | The last time this balance was updated. |
| `raw` | `jsonb` | | The raw, unprocessed balance data. |

**Constraints:**
- Unique constraint on `(broker_account_id)`

## Microservice Responsibilities

The Stream Bridge microservice will:
- Subscribe to multiple real-time data streams.
- Normalize the data from these streams into the schemas defined above.
- Write the normalized data to the Supabase database in batches.
- Handle connection errors and retries gracefully.

## Deployment

The Stream Bridge will be a standalone Python service, containerized with Docker. It can be deployed as a long-running process in a VM, a Kubernetes pod, or as a Cloud Run service (if the streams are request-based).

## Non-Goals / Open Questions

- The exact WebSocket URLs and authentication credentials for the Developer Console streams are not yet defined and will need to be provided as environment variables.
- The service is currently designed to be a simple bridge. More complex logic, such as L2 order book management, is out of scope for this initial implementation.
