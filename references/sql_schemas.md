# Drillr SQL Schemas — Discovery Guide

Drillr's `run_sql` exposes a curated set of tables. **The available
table list evolves**, and there is no public catalog mapping
"financial statement type" → "table name". Do not hard-code table
names from memory — discover them at runtime.

This file is loaded only when you need to write `run_sql`. For tool
syntax, see `references/tools.md`.

---

## Golden rule — discover, don't guess

Before writing any `run_sql`:

1. Use `list_tables` to enumerate alt-data tables in a category, OR
   try `get_table_schema --query "table_name=<candidate>"` for tables
   you already know by name (only `price_volume_history` is reliably
   present today).
2. **If `get_table_schema` returns `columns: []` (empty array), treat
   the table as non-existent.** This is the current gateway behavior
   for unknown tables — it returns 200 with empty columns instead of
   404. Move on; don't try `run_sql` against it.
3. If a `run_sql` query returns `400 invalid_request "relation \"X\"
   does not exist"`, the table is gone or never existed. Don't retry
   with variants like `<name>_v2` or `financial_<name>` — those are
   guesses. Switch strategy (see fallback below).

## When numeric financials aren't in SQL — use SEC filing text

If the user asks for standardized financials (income statement, gross
margin, EPS, balance-sheet items) and you can't find a table for it
via `list_tables` + `get_table_schema`, **switch to
`sec_report_search`**:

```bash
python scripts/drillr.py call sec_report_search \
  --json '{"ticker":"AAPL","query":"gross margin and operating margin","top_k":5}'
```

10-Q / 10-K filings contain the structured financial tables as
embedded text and tables. Vector search returns paragraph-level
snippets with citation metadata; extract the numbers from there and
quote the filing period + form type in your answer.

This is the **canonical path** for standardized fundamentals when
SQL coverage is incomplete. Don't apologize for it — it's how drillr
sources the same data the SQL layer would, just via the filing
upstream.

## What is reliably in SQL today

### `price_volume_history` — OHLCV

Confirmed columns (via `get_table_schema`):

- `id` (text), `ticker` (text), `period_end` (date),
  `time_frame` (text — `daily` / `weekly` / `monthly`),
  `open`, `high`, `low`, `close`, `volume` (numeric)

Always project columns explicitly; never `SELECT *` over the full
table.

### Alt-data tables — discoverable via `list_tables`

Categories include (non-exhaustive): `Twitter`, `Reddit`,
`AI Models`, `AI Companies`, `AI Benchmarks`, `LLM Token Pricing`,
`Compute`, `Energy and Power`, `Data Centers`, `Semiconductors`,
`Macro and Trade`, `Critical Minerals`, `Prediction Markets`.

Workflow:

```bash
python scripts/drillr.py call list_tables --query "categories=AI%20Models"
# → response lists {name, summary} for each table in the category
python scripts/drillr.py call get_table_schema --query "table_name=<chosen>"
# → check it returns non-empty columns before writing SQL
python scripts/drillr.py call run_sql --json '{"sql":"SELECT ... FROM <chosen> WHERE ..."}'
```

## SQL hard rules

- **`SELECT` only.** `INSERT` / `UPDATE` / `DROP` / DDL / any other
  statement returns `400 invalid_request`.
- **No `information_schema` / `pg_*`.** The gateway blocks system
  catalog access with `400 invalid_request "Access to
  information_schema / pg_* system catalogs is not allowed"`. Do not
  try to query metadata that way; use `list_tables` /
  `get_table_schema` instead.
- **No multi-statement queries.**
- **Joins, CTEs, window functions, aggregation** all supported.
- **Currency is USD** unless the table has an explicit `currency` column.

## Quick recipes — only for tables you've verified exist

### Recent daily closes

```sql
SELECT period_end, close, volume
FROM price_volume_history
WHERE ticker='AAPL' AND time_frame='daily'
ORDER BY period_end DESC LIMIT 30
```

### Two-ticker price comparison

```sql
SELECT ticker, period_end, close
FROM price_volume_history
WHERE ticker IN ('AMD','NVDA') AND time_frame='daily'
  AND period_end >= '2026-01-01'
ORDER BY ticker, period_end DESC
```

> The earlier version of this file listed table names like
> `income_statement`, `profitability_ratios`, `valuation_ratios`,
> `insider_trades`. **Those names did not work against the live
> database** in 2026-05 testing. Until this file is updated with
> verified names, treat SQL as alt-data + prices only, and route
> fundamentals through `sec_report_search`.
