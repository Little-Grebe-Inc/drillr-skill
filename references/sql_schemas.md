# Drillr SQL Schemas — Discovery Guide

Drillr exposes 90+ standardized tables across two universes:

1. **Standardized financials** — income statements, balance sheets,
   cash flows, ratios, prices, earnings, insider, ownership. Use
   directly with `get_table_schema` + `run_sql`. These are **not**
   surfaced via `list_tables` (which is alt-data only).
2. **Alt-data** — AI value chain, energy, semiconductors, macro &
   trade, social signals, prediction markets, etc. Discover these
   with `list_tables` then `get_table_schema`.

This file is loaded only when you need to write `run_sql`. For tool
syntax, see `references/tools.md`.

---

## Discovery workflow

Don't guess table names — they change. Two paths:

**Path A · Standardized financials** (known table name)

```bash
# Inspect columns first
python scripts/drillr.py call get_table_schema --query "table_name=income_statement"
# Then query
python scripts/drillr.py call run_sql --json '{"sql":"SELECT ... FROM income_statement WHERE ..."}'
```

**Path B · Alt-data** (table name unknown)

```bash
# Find tables in a category
python scripts/drillr.py call list_tables --query "categories=AI%20Models,Compute"
# Pick a table, inspect schema
python scripts/drillr.py call get_table_schema --query "table_name=<the_one>"
# Query
python scripts/drillr.py call run_sql --json '{"sql":"..."}'
```

---

## Common standardized financial tables

The catalog evolves — confirm column names via `get_table_schema`
before relying on them. This list is a starting map, not a contract.

### Pricing & market data

| Table                  | Holds                                                       |
| ---------------------- | ----------------------------------------------------------- |
| `price_volume_history` | OHLCV by ticker × time_frame (`daily`, `weekly`, `monthly`) |

### Fundamentals (quarterly + annual)

| Table                  | Holds                                                        |
| ---------------------- | ------------------------------------------------------------ |
| `income_statement`     | Revenue, COGS, gross margin, operating income, EPS, etc.     |
| `balance_sheet`        | Assets, liabilities, equity, cash, debt                      |
| `cash_flow_statement`  | Operating / investing / financing cash flows, FCF            |
| `valuation_ratios`     | P/E, P/S, P/B, EV/EBITDA, dividend yield                     |
| `profitability_ratios` | Gross / operating / net margin, ROE, ROA, ROIC               |
| `growth_metrics`       | YoY / QoQ growth on revenue, earnings, etc.                  |

Common filter columns:

- `ticker` — string
- `fiscal_period` — `Q` (quarterly) or `A` (annual)
- `fiscal_year`, `fiscal_quarter`
- `period_end` — date (calendar end of fiscal period)

> Tip: when the user says "Q3 2026", confirm with `fiscal_utility`
> that you know which calendar months that maps to — fiscal calendars
> differ by ticker.

### Earnings

| Table                  | Holds                                                        |
| ---------------------- | ------------------------------------------------------------ |
| `earnings_calendar`    | Upcoming + historical earnings dates, estimates              |
| `earnings_call_summaries` | AI-structured summaries (guidance, risks, segments, Q&A)  |

### Analyst coverage

| Table                  | Holds                                                        |
| ---------------------- | ------------------------------------------------------------ |
| `analyst_ratings`      | Rating events from major sell-side firms                     |
| `analyst_consensus`    | Consensus rollups: target, rating distribution               |

### Ownership & insider activity

| Table                  | Holds                                                        |
| ---------------------- | ------------------------------------------------------------ |
| `insider_trades`       | Form 3/4/5 — by ticker, by insider, by date                  |
| `institutional_holdings` | 13F-HR / 13D / 13G filings                                 |

### Company metadata

| Table                  | Holds                                                        |
| ---------------------- | ------------------------------------------------------------ |
| `company_profile`      | Sector, industry, country, listing exchange, description     |
| `index_membership`     | S&P 500 / NASDAQ-100 / etc. membership over time             |

---

## Alt-data categories

These ship through `list_tables`. Categories include (non-exhaustive):

- `Twitter`, `Reddit` — social
- `AI Models`, `AI Companies`, `AI Benchmarks`, `LLM Token Pricing` —
  AI ecosystem
- `Compute`, `Energy and Power`, `Data Centers`, `Semiconductors` —
  AI value chain infrastructure
- `Macro and Trade`, `Critical Minerals` — geopolitics / commodities
- `Prediction Markets` — Polymarket, Kalshi event probabilities

Call `list_tables` with 1-5 categories per request to get the
table-name + description tuples.

---

## SQL conventions

- All tables use `ticker` (uppercase) as the primary equity key.
- Time-series tables use `period_end` (date) or `event_time`
  (timestamp); confirm via `get_table_schema`.
- `time_frame` on price tables is one of: `daily`, `weekly`, `monthly`,
  `intraday_5m` (where supported).
- Currency is USD unless a table is explicitly cross-currency (look
  for a `currency` column).

## SQL safety

- Only `SELECT` is permitted. `INSERT` / `UPDATE` / `DROP` / DDL
  return `400 invalid_request`.
- Multi-statement queries are rejected.
- Aggregation, joins, CTEs, window functions are supported.

## Quick recipes

### Last 4 quarters of gross margin for a ticker

```sql
SELECT period_end, gross_margin
FROM profitability_ratios
WHERE ticker='AAPL' AND fiscal_period='Q'
ORDER BY period_end DESC LIMIT 4
```

### Compare two tickers on one metric

```sql
SELECT ticker, period_end, gross_margin
FROM profitability_ratios
WHERE ticker IN ('AMD','NVDA') AND fiscal_period='Q'
  AND period_end >= '2025-01-01'
ORDER BY ticker, period_end DESC
```

### Recent insider buys for a ticker

```sql
SELECT trade_date, insider_name, transaction_type, shares, price
FROM insider_trades
WHERE ticker='NVDA' AND trade_date >= '2026-01-01'
ORDER BY trade_date DESC LIMIT 50
```

### Top S&P 500 by 1-month return

```sql
SELECT p.ticker,
       MAX(p.close) FILTER (WHERE p.period_end = CURRENT_DATE - INTERVAL '1 day') /
       MAX(p.close) FILTER (WHERE p.period_end = CURRENT_DATE - INTERVAL '30 days') - 1 AS ret_1m
FROM price_volume_history p
JOIN index_membership im ON im.ticker=p.ticker AND im.index_name='S&P 500'
WHERE p.time_frame='daily'
GROUP BY p.ticker
ORDER BY ret_1m DESC LIMIT 20
```

> Confirm exact column names with `get_table_schema` — these recipes
> are pattern templates, not guaranteed-correct code.
