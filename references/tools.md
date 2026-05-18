# Drillr Tools — Detailed Reference

This file is loaded only when the agent needs exact parameter shapes,
response schemas, or credit costs. For high-level guidance, see
`SKILL.md`. For SQL table discovery, see `sql_schemas.md`.

All tools are invoked via the dispatcher:

```bash
python scripts/drillr.py call <tool> --json '<body>'    # POST
python scripts/drillr.py call <tool> --query '<qs>'     # GET (raw)
python scripts/drillr.py call <tool> --json '<obj>'     # GET (auto-converted)
```

Stdout = JSON response. Stderr = structured error (`LABEL: msg`).
Exit codes: see `SKILL.md › Error handling`.

REST mirror: every tool maps 1:1 to `POST|GET https://gateway.drillr.ai/api/v1/data/<tool>`.

---

## `run_sql` — Standardized financial SQL (POST)

Execute a read-only `SELECT` against the standardized data layer.

**Body:**

```json
{ "sql": "SELECT ticker, period_end, gross_margin FROM income_statement WHERE ticker='AAPL' AND fiscal_period='Q' ORDER BY period_end DESC LIMIT 4" }
```

| Field | Required | Notes                                              |
| ----- | -------- | -------------------------------------------------- |
| `sql` | yes      | Non-empty `SELECT`. Anything else returns `400`.   |

**Response shape:**

```json
{
  "data": { "columns": ["..."], "rows": [["..."]], "rowCount": <int> },
  "_credits": { "charged": <int>, "method": "...", "balance_after": <int> }
}
```

**Tips:**

- Use single-quote escaping inside JSON: `\"ticker='AAPL'\"`.
- Discover tables with `list_tables` and `get_table_schema` before
  writing SQL — table names change as the catalog evolves.
- The query budget per call is bounded; very wide `SELECT *` over many
  rows may time out. Project columns explicitly.

---

## `sec_report_search` — Semantic search inside SEC filings (POST)

Paragraph-level search over indexed filings (10-K / 10-Q / 20-F / 6-K
/ S-1 / DEF 14A).

**Body:**

```json
{
  "ticker": "NVDA",
  "query": "export license risk on H100 / H200",
  "top_k": 8,
  "period_start": "2024-01",
  "period_end": "2026-05",
  "filing_types": ["10-K", "10-Q"]
}
```

| Field          | Required | Notes                                                         |
| -------------- | -------- | ------------------------------------------------------------- |
| `ticker`       | yes      | Single ticker                                                 |
| `query`        | yes      | Natural-language search query                                 |
| `top_k`        | no       | 1-30, default ~10                                             |
| `period_start` | no       | `YYYY-MM`                                                     |
| `period_end`   | no       | `YYYY-MM`                                                     |
| `filing_types` | no       | Array, e.g. `["10-K","10-Q"]`. Omit for all.                  |

**Response:** ordered array of matches with `score`, `node_id`,
paragraph text, and filing-period metadata. Quote selectively — these
are extracts, not summaries.

---

## `company_search` — Resolve / discover companies (POST)

Maps natural-language descriptions or ticker fragments to candidate
tickers, with `match_reason`.

**Body:**

```json
{ "query": "AI infrastructure leaders with US listings" }
```

| Field   | Required | Notes                                              |
| ------- | -------- | -------------------------------------------------- |
| `query` | yes      | Natural language: name, ticker, theme, or business |

**Response:** `{ data: { query, results: [{ ticker, company_name, match_reason, ... }] } }`.

**Use it:**

- When the user names a company but no ticker (`"Apple"` → `AAPL`).
- For thematic / sector discovery (`"lithium miners"`, `"AI value
  chain"`) before drilling into specific tickers.

---

## `sec_report_list` — Filings catalog by ticker (GET)

**Query params:**

| Param          | Required | Notes                                            |
| -------------- | -------- | ------------------------------------------------ |
| `ticker`       | yes      | Single ticker                                    |
| `filing_types` | no       | CSV: `10-K,10-Q,8-K,20-F,6-K,S-1,DEF 14A`        |
| `limit`        | no       | Max items returned                               |

**Use it:** to find the most recent filing(s) of a type before
running `sec_report_search` constrained to that period.

---

## `signal_list` — Curated cross-asset event feed (GET)

**Query params (all optional):**

| Param        | Notes                                                             |
| ------------ | ----------------------------------------------------------------- |
| `tickers`    | CSV — `NVDA,AAPL,MSFT`                                            |
| `sector`     | CSV — `information_technology,health_care` (snake_case lowercase) |
| `from_date`  | ISO 8601, e.g. `2026-05-01T00:00:00Z`                             |
| `to_date`    | ISO 8601                                                          |
| `order_by`   | `created_at` (default) or `earliest_trigger_event_time`           |
| `limit`      | 1-100, default 20                                                 |
| `offset`     | Default 0                                                         |

**Response items** carry `headline`, `summary`, `suggested_tickers`,
`sector`, `score`, `trigger_sources[]` (with `source_url` /
`source_name`), `earliest_trigger_event_time`, `tags`.

**Score ≥ 3** is "noteworthy". Score 1-2 is background.

---

## `list_tables` — Discover alt-data tables (GET)

**Query params:**

| Param        | Required | Notes                                                |
| ------------ | -------- | ---------------------------------------------------- |
| `categories` | yes      | CSV, 1-5 categories per call                         |

Categories include (non-exhaustive): `Twitter`, `Reddit`, `AI Models`,
`AI Companies`, `AI Benchmarks`, `LLM Token Pricing`, `Compute`,
`Energy and Power`, `Data Centers`, `Semiconductors`, `Macro and
Trade`, `Critical Minerals`, `Prediction Markets`.

**Response:** `{ data: [{ category, tables: [{ name, description }] }] }`.

For standardized financial tables (income statements, ratios, prices,
etc.), use `get_table_schema` directly — they're not surfaced via
`list_tables` which is alt-data-only.

---

## `get_table_schema` — Inspect a SQL table (GET)

**Query params:**

| Param        | Required | Notes                                       |
| ------------ | -------- | ------------------------------------------- |
| `table_name` | yes      | Exact table name as returned by `list_tables`, or a known standardized table (e.g. `income_statement`, `valuation_ratios`, `price_volume_history`) |

**Response:** `{ data: { table, columns: [{ column_name, data_type, comment }] } }`.

**Use it** before writing `run_sql` to confirm column names and types.

---

## `fiscal_utility` — Fiscal ↔ calendar period mapping (GET)

Companies with non-calendar fiscal years (e.g. NVDA = Jan, AAPL =
Sept) require this to convert between user-spoken periods ("Q3") and
calendar dates used in SQL.

**Query params:**

| Param            | Notes                                                  |
| ---------------- | ------------------------------------------------------ |
| `ticker`         | Required                                               |
| `yyyy_mm`        | Reverse mode: given a calendar month → return fiscal   |
| `fiscal_year`    | Forward mode: given fiscal year (and optional quarter) |
| `fiscal_quarter` | 0 = full year, 1-4 = quarter. Required in forward mode |

**Two modes:**

- Forward: supply `fiscal_year` + `fiscal_quarter` → returns calendar
  date range
- Reverse: supply `yyyy_mm` → returns which fiscal year/quarter the
  month falls into for that ticker

---

## Credit accounting

Every successful 2xx response carries `_credits.charged` and
`_credits.balance_after`. Typical costs:

- `signal_list`, `list_tables`, `get_table_schema`, `fiscal_utility`,
  `sec_report_list`: 1-2 cr / call
- `run_sql`: 1 cr / call (independent of result size)
- `company_search`: 1-3 cr / call
- `sec_report_search`: 3-6 cr / call (vector search is the costliest)

Watch `balance_after` over time. If it drops fast, the user can top up
at <https://drillr.ai/developer/keys>.

Rate limit: ~30 req/min per key. On `429`, the dispatcher exits with
code `4` (`RATE_LIMIT`). Sleep ~30s and retry.
