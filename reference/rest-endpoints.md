# drillr Public Data API v2 — endpoint reference

Generated from https://gateway.drillr.ai/api/v2/openapi.json (`2.0.0-spec.110`) by `scripts/gen-reference.py`. Do not edit by hand.

Base URL `https://gateway.drillr.ai` — every path below is absolute under it. Auth header `X-API-KEY: drl_…` (create at https://drillr.ai/account/api-keys). Rate limit 100 requests/min per key. Responses are `{"data": [rows]}`; every row derived from a disclosure links to the source filing. Full pages with response fields and worked examples: https://drillr.ai/docs/api/<endpoint>.

## Company

Ticker resolution, natural-language company discovery and company profiles

### `GET /api/v2/tickers` — Resolve or list canonical tickers

Converts a company name, local code, ISIN, CIK or CUSIP into the `ticker` that every other endpoint uses, one per row. Without `query`, lists all currently trading common stocks in a market. Call this first when you only have a name or an identifier.

Cost **0.02 cr per call** · refresh: weekdays; profile 07:00 UTC, snapshot 16:00 UTC · docs: https://drillr.ai/docs/api/tickers

| param | required | type / values |
|---|---|---|
| `query` |  | string |
| `market` |  | csv of `US`, `CN`, `JP` |
| `limit` |  | integer, default `10`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/tickers?query=Apple%20Inc.&market=US`

### `GET /api/v2/company-discovery` — Discover companies from a natural-language description

Finds companies from a plain-language description. Returns every candidate that passes verification, one company per row: the ticker, the company name and the reason it matched. Use it when you do not know the ticker, then call the other endpoints with what it returns.

Cost **3 cr per call** · refresh: follows company snapshot rebuild · docs: https://drillr.ai/docs/api/company-discovery

| param | required | type / values |
|---|---|---|
| `query` | yes | string |
| `market` |  | csv of `US`, `CN`, `JP`, `HK`, `KR` |

Example: `GET /api/v2/company-discovery?query=US%20companies%20that%20design%20GPUs%20for%20data%20centers&market=US`

### `GET /api/v2/company-profile` — Get company profiles

Returns basic company profiles and external identifiers, one row per company. For prices, use `/prices-snapshot`; for valuation, use `/financial-metrics-snapshot`.

Cost **0.02 cr per call** · refresh: weekdays; profile 07:00 UTC, snapshot 16:00 UTC · docs: https://drillr.ai/docs/api/company-profile

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 50) |

Example: `GET /api/v2/company-profile?ticker=AAPL`

## Filings

Regulatory filing lists and full-text filing search (US, Japan, China)

### `GET /api/v2/filings` — List retained regulatory filings

Returns a company's filings, one row per filing, with the form type, filing date and a link to the official document. Ordered by `filing_date` descending, then `accession_number` descending for the same day. Covers the last 5 years for US and the last 3 years of financial reports for JP / CN; there are no date or form-type parameters and no market-wide scan — every filing for that company inside the window comes back together. Filter for annual or quarterly reports yourself on the `form_type` field of the returned rows.

Cost **0.02 cr per call** · refresh: US 5m; JP 15-30m; CN daily 16:00 UTC · docs: https://drillr.ai/docs/api/filings

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 10) |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/filings?ticker=AAPL&limit=20`

### `GET /api/v2/filing-search` — Search retained filing text for one company

Search SEC filings and Chinese and Japanese financial reports for facts buried in footnotes, tables and narrative disclosures. Semantic and keyword search returns original passages with filing context.

Cost **0.1 cr per call** · refresh: US 5m; JP 15-30m; CN daily 16:00 UTC · docs: https://drillr.ai/docs/api/filing-search

| param | required | type / values |
|---|---|---|
| `query` | yes | string |
| `ticker` | yes | csv of string (max 1) |
| `form_type` |  | string |
| `from` |  | string `^\d{4}-(0[1-9]|1[0-2])$` |
| `to` |  | string `^\d{4}-(0[1-9]|1[0-2])$` |
| `limit` |  | integer, default `10`, max 50 |

Example: `GET /api/v2/filing-search?ticker=AAPL&query=share+repurchase&form_type=10-K&from=2025-01&to=2025-12`

## Signal

Industry inflections, enterprise AI adoption and cross-source news search

### `GET /api/v2/industry-inflections` — List published industry inflections

Returns industry-level changes synthesized from the earnings calls of multiple US-listed companies, one row per inflection theme that can be tracked over time: the change mechanism, impact scope and degree, market attention, and the per-company impact breakdown (the `company_impacts` array, not flattened by company). Built from earnings calls held after July 2026 and refreshed daily as new calls and evidence arrive.

Cost **1 cr per call** · refresh: daily upstream research refresh and historical replay · docs: https://drillr.ai/docs/api/industry-inflections

| param | required | type / values |
|---|---|---|
| `keyword` |  | string |
| `ticker` |  | csv of string (max 10) |
| `limit` |  | integer, default `10`, max 10 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/industry-inflections?limit=10&page=1`

### `GET /api/v2/enterprise-ai-adoption` — List enterprise AI adoption observations

Returns the concrete enterprise AI applications US-listed companies have disclosed on earnings calls: the workflow each is used in, its deployment stage and scope, the value disclosed, metrics and supporting evidence. General statements about AI strategy are excluded.

Cost **1 cr per call** · refresh: daily upstream research refresh and historical replay · docs: https://drillr.ai/docs/api/enterprise-ai-adoption

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `since` |  | string (date-time) |
| `limit` |  | integer, default `10`, max 10 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/enterprise-ai-adoption?ticker=ALHC&since=2024-01-01`

### `POST /api/v2/news-search` — Search cross-source news storylines, events and attributed claims

Searches news across sources and returns storylines. Duplicate reports of the same occurrence are merged into one event, related events are grouped into a storyline, and statements with a named speaker and subject are returned separately as attributed claims (`claims`). Each item in `results` is a storyline, not an article; every result is an in-house summary with links to the original sources, and article text is not included.

Cost **1 cr per call** · refresh: continuous signal ingestion · docs: https://drillr.ai/docs/api/news-search

JSON body:

| field | required | type / values |
|---|---|---|
| `query` |  | string |
| `theme` |  | string |
| `ticker` |  | string | csv of string (max 1) |
| `since` |  | string (date-time) |
| `until` |  | string (date-time) |
| `search_type` |  | `all`, `events`, `claims` |
| `order_by` |  | `relevance`, `event_time`, `create_time` |
| `top_k` |  | integer, default `10`, max 50 |
| `cursor` |  | string |

At least one of: `query`, `theme`, `ticker`, `since`, `until`.

Example body:

```json
{
  "query": "export controls",
  "ticker": "NVDA",
  "search_type": "all",
  "order_by": "relevance",
  "top_k": 2
}
```

## Financials

The three financial statements and precomputed financial metrics

### `GET /api/v2/income-statements` — Get income statements

Returns a company's income statement: revenue, costs, profit at each level, earnings per share and more, one row per reporting period. 29 line-item columns in total, plus the 14 meta-data fields shared by the three statements, all listed under Response fields. `ebitda` is a derived column (not an as-reported line). Quarterly amounts may be calculated from cumulative disclosures; earnings per share and weighted average shares cannot be obtained by directly subtracting cumulative figures.

Cost **0.02 cr per call** · refresh: follows filing ingestion; canonical replay weekly · docs: https://drillr.ai/docs/api/income-statements

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 10) |
| `period` |  | csv of `FY`, `Q1`, `Q2`, `Q3`, `Q4` |
| `limit` |  | integer, default `4`, max 40 |

Example: `GET /api/v2/income-statements?ticker=AAPL&period=FY&limit=5`

### `GET /api/v2/balance-sheets` — Get balance sheets

Returns a company's balance sheet: assets, liabilities, shareholders' equity and their line items, one row per reporting period as of period end. 41 line-item columns in total, plus the 14 meta-data fields shared by the three statements, all listed under Response fields; `period_start` is always `null`. `total_debt` / `net_debt` are derived columns (not as-reported lines); all other columns are as-reported values.

Cost **0.02 cr per call** · refresh: follows filing ingestion; canonical replay weekly · docs: https://drillr.ai/docs/api/balance-sheets

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 10) |
| `period` |  | csv of `FY`, `Q1`, `Q2`, `Q3`, `Q4` |
| `limit` |  | integer, default `4`, max 40 |

Example: `GET /api/v2/balance-sheets?ticker=AAPL&period=FY&limit=3`

### `GET /api/v2/cash-flow-statements` — Get cash-flow statements

Returns a company's cash flow statement: operating, investing and financing cash flows plus free cash flow, one row per reporting period. 16 line-item columns in total, plus the 14 meta-data fields shared by the three statements, all listed under Response fields. Signs follow the statement direction: outflows such as capital expenditures, buybacks and dividends are negative, inflows such as investment proceeds are positive. `free_cash_flow` is a derived column (not an as-reported line). Quarterly cash flows may be calculated from cumulative disclosures; half-year or full-year cumulative amounts are not returned as single-quarter amounts.

Cost **0.02 cr per call** · refresh: follows filing ingestion; canonical replay weekly · docs: https://drillr.ai/docs/api/cash-flow-statements

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 10) |
| `period` |  | csv of `FY`, `Q1`, `Q2`, `Q3`, `Q4` |
| `limit` |  | integer, default `4`, max 40 |

Example: `GET /api/v2/cash-flow-statements?ticker=AAPL&period=FY&limit=3`

### `GET /api/v2/financial-metrics-snapshot` — Get current financial metrics

Returns a company's precomputed valuation and financial ratios: market cap, enterprise value, TTM valuation multiples, margins, returns, growth rates, leverage and liquidity ratios, and dividend metrics, one row per ticker as of the latest snapshot date. Ratios are always decimals (`0.25` = 25%), not percentages; monetary fields are in `currency` (the trading currency), and `market_capitalization_usd` is additionally converted to USD at the snapshot-date rate.

Cost **0.02 cr per call** · refresh: weekdays at 16:00 UTC · docs: https://drillr.ai/docs/api/financial-metrics-snapshot

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 50) |

Example: `GET /api/v2/financial-metrics-snapshot?ticker=AAPL`

## Prices

Historical bars and latest closing-price snapshots (US)

### `GET /api/v2/prices-historical` — Get US daily, weekly or monthly price history

Returns a stock's historical daily, weekly or monthly bars: open, high, low and close, one row per bar, in descending `date` order. All bars in the date window come back in a single response; `limit` / `page` are not accepted. Prices are raw and unadjusted, updated after market close; there is no intraday or real-time data.

Cost **0.02 cr per call** · refresh: weekdays after close at 22:00 UTC · docs: https://drillr.ai/docs/api/prices-historical

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 1) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `interval` |  | `day`, `week`, `month` |

Example: `GET /api/v2/prices-historical?ticker=AAPL&from=2026-01-01&to=2026-08-20&interval=week`

### `GET /api/v2/prices-snapshot` — Get latest US closing-price snapshots

Returns each stock's closing price for its latest trading day, at most one row per ticker, with `date` as that trading day. Prices are unadjusted and updated after market close; this is not a real-time quote. Row order is not declared in the contract, so match rows to the request by the `ticker` field, not by position. US common stock only: if any ticker cannot be resolved or is non-US, the whole request returns `404` rather than returning what it can and silently dropping the rest. For historical prices use `/prices-historical`.

Cost **0.02 cr per call** · refresh: weekdays after close at 22:00 UTC · docs: https://drillr.ai/docs/api/prices-snapshot

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 50) |

Example: `GET /api/v2/prices-snapshot?ticker=AAPL,MSFT`

## Earnings

Earnings calendar and structured earnings-call summaries

### `GET /api/v2/earnings-calendar` — Get earnings calendar entries

Returns the earnings calendar for a date range: which company reports on which day, with EPS / revenue estimates and actuals. One row per company per announcement, covering US / CN / JP, queried by announcement date `date`; there is no ticker filter, so filter the returned rows for a single company.

Cost **0.02 cr per call** · refresh: hourly · docs: https://drillr.ai/docs/api/earnings-calendar

| param | required | type / values |
|---|---|---|
| `from` | yes | string (date) |
| `to` | yes | string (date) |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/earnings-calendar?from=2026-03-06&to=2026-06-03&limit=50&page=1`

### `GET /api/v2/earnings-call-summary` — Get earnings-call summaries

Returns a structured summary of an earnings call across five dimensions: management highlights, guidance, risks, segment performance and Q&A topics, plus the title and date, one row per call; the transcript itself is not provided. Locate a call with `ticker` + `fiscal_year` + `period`; a fiscal quarter usually has only one call, so the default `limit=1` is enough.

Cost **0.02 cr per call** · refresh: transcripts every 10m; summary follows ingestion · docs: https://drillr.ai/docs/api/earnings-call-summary

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 1) |
| `fiscal_year` | yes | integer |
| `period` | yes | csv of `Q1`, `Q2`, `Q3`, `Q4`, `FY` |
| `limit` |  | integer, default `1`, max 20 |

Example: `GET /api/v2/earnings-call-summary?ticker=AAPL&fiscal_year=2020&period=Q3`

## Ownership

Insider holdings and transactions, institutional holdings (US only)

### `GET /api/v2/insider-trades` — Get self-parsed insider holdings and transactions

Query insiders' initial holdings and transactions for a company. Each row represents one Form 3 initial holding or one Form 4 / Form 5 transaction, including amended filings.

Cost **0.02 cr per call** · refresh: daily 11:00 UTC plus weekly replay · docs: https://drillr.ai/docs/api/insider-trades

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 1) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `record_type` |  | csv of `initial_holding`, `transaction` |
| `form_type` |  | csv of `3`, `3/A`, `4`, `4/A`, `5`, `5/A` |
| `transaction_type` |  | csv of `buy`, `sell`, `award`, `exercise`, `tax_withholding`, `other` |
| `is_amendment` |  | boolean |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/insider-trades?ticker=AAPL&from=2026-07-01&to=2026-08-31&transaction_type=sell&is_amendment=false`

### `GET /api/v2/institutional-holdings` — Get self-parsed institutional holdings

Query institutional investors’ reported quarterly holdings, quantities and market values. Each row is one holding record from an SEC 13F-HR filing or amendment, rather than an aggregated institution–security position.

Cost **0.02 cr per call** · refresh: daily 05:00 UTC plus weekly replay · docs: https://drillr.ai/docs/api/institutional-holdings

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 1) — One of ticker, investor_cik is required. |
| `investor_cik` |  | string — One of ticker, investor_cik is required. |
| `report_period` |  | string (date) |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/institutional-holdings?investor_cik=0001067983&report_period=2026-06-30`

## Events

Corporate events: financings, deals, executive changes, corporate actions, ownership (US only)

### `GET /api/v2/events` — Get the canonical company-event timeline

Returns a company's event timeline: financings, deals, executive changes, dividends and buybacks, ownership changes, bankruptcy and delisting. Each row contains shared fields such as the event date, classification and filing link. Type-specific fields such as deal terms are on the matching `/events-*` endpoint: choose it by `event_class`, query with the same `ticker` and `from` = `to` = `event_date`, then match on `event_id` (identical on both sides; typed endpoints do not accept an `event_id` parameter).

Cost **0.02 cr per call** · refresh: intraday extraction plus Sunday 09:00 UTC canonical replay · docs: https://drillr.ai/docs/api/events

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `event_class` |  | csv of `capital`, `distribution`, `share_structure`, `transaction`, `agreement`, `governance`, `ownership`, `legal_regulatory` |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/events?ticker=BA&event_class=capital&from=2026-08-01&to=2026-08-31`

### `GET /api/v2/events-financings` — Get financing events

Returns a company's financing events with their terms: equity issuances, debt issuances, convertible notes, guarantees and defaults, one row per event (`event_class = capital`), distinguished by `event_type`, with amount, interest rate, maturity, issue price and other terms in type-specific fields. Buybacks are not here; they belong to `/events-corporate-actions`.

Cost **0.02 cr per call** · refresh: intraday extraction plus Sunday 09:00 UTC canonical replay · docs: https://drillr.ai/docs/api/events-financings

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `event_type` |  | csv of `equity_issuance`, `debt_issuance`, `convertible`, `guarantee`, `debt_default` |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/events-financings?ticker=BA&event_type=debt_issuance&from=2026-08-01&to=2026-08-31`

### `GET /api/v2/events-deals` — Get deal events

Returns a company's deals and agreements with counterparties: M&A, divestitures, joint ventures, licensing, material contracts and settlements, one row per deal (`event_class = transaction` or `agreement`), with the filing company as the subject: `direction` / `filer_role` state whether it is buyer or seller, licensor or licensee, and the counterparty is in `counterparty_names` / `counterparty_tickers`.

Cost **0.02 cr per call** · refresh: intraday extraction plus Sunday 09:00 UTC canonical replay · docs: https://drillr.ai/docs/api/events-deals

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `event_class` |  | csv of `transaction`, `agreement` |
| `event_type` |  | csv of `acquisition`, `disposal`, `merger`, `spin_off`, `joint_venture`, `strategic_investment`, `restructuring`, `license`, `supply`, `partnership`, `major_contract`, `settlement` |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/events-deals?ticker=MSFT&event_type=acquisition&from=2023-10-01&to=2023-10-31`

### `GET /api/v2/events-executive-changes` — Get executive-change events

Returns changes among a company's executives, directors and auditors: who, which role, appointment or departure, and the effective date, one row per change (`executive_change` / `director_change` / `auditor_change` within `event_class = governance`). Only disclosed facts are restated, with no profiling of individuals. Equity incentive events (`equity_incentive`) are available only on the `/events` timeline.

Cost **0.02 cr per call** · refresh: intraday extraction plus Sunday 09:00 UTC canonical replay · docs: https://drillr.ai/docs/api/events-executive-changes

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `event_type` |  | csv of `executive_change`, `director_change`, `auditor_change` |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/events-executive-changes?event_type=executive_change&from=2026-03-01&to=2026-03-31`

### `GET /api/v2/events-corporate-actions` — Get corporate-action events

Returns the dividends, buybacks, capital reductions, splits and reverse splits, stock dividends and bonus issues, and share class changes a company has announced, one row per disclosure (`event_class = distribution` or `share_structure`). It records what the company announced and is not a source of adjustment factors: no rights-issue / spin-off ex-date adjustment parameters are provided, and `/prices-historical` returns unadjusted prices.

Cost **0.02 cr per call** · refresh: intraday extraction plus Sunday 09:00 UTC canonical replay · docs: https://drillr.ai/docs/api/events-corporate-actions

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `event_class` |  | csv of `distribution`, `share_structure` |
| `event_type` |  | csv of `dividend`, `buyback`, `capital_reduction`, `stock_split`, `reverse_split`, `bonus_issue`, `share_class_change` |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/events-corporate-actions?ticker=AVGO&event_type=dividend&from=2026-09-01&to=2026-09-30`

### `GET /api/v2/events-ownership` — Get ownership events

Returns major shareholder positions disclosed in SEC Schedule 13D/G filings. Each row represents one reporting person and security position in a filing, with the currently reported ownership, its change from the preceding filing when calculable, and a link to the official document; a joint filing can return multiple rows. Only the latest row for each company + shareholder + security sequence is returned. `event_class` is fixed at `ownership` and `event_type` at `stake_change`. For routine insider trades, use `/insider-trades`.

Cost **0.02 cr per call** · refresh: intraday extraction plus Sunday 09:00 UTC canonical replay · docs: https://drillr.ai/docs/api/events-ownership

| param | required | type / values |
|---|---|---|
| `ticker` |  | csv of string (max 10) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/events-ownership?ticker=PLTR&from=2026-03-01&to=2026-03-31`

## Analyst

Analyst consensus and individual rating events (US only)

### `GET /api/v2/analyst-consensus` — Get self-built analyst consensus

Returns the analyst consensus for a stock: the five-tier distribution (strong buy to strong sell) of each firm's latest rating within the last 90 days, plus the mean / high / low price target, one row per ticker. Aggregated results only; this platform's own ratings are not included.

Cost **0.02 cr per call** · refresh: daily 23:00 UTC · docs: https://drillr.ai/docs/api/analyst-consensus

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 50) |

Example: `GET /api/v2/analyst-consensus?ticker=NVDA,AMD`

### `GET /api/v2/analyst-ratings` — Get self-parsed analyst rating events

Returns individual analyst rating and price target changes: which firm upgraded, downgraded or maintained a rating on which day, and what the price target moved from and to, one row per event, ordered by `date desc, published_at desc`. Sourced from news reports; every row carries the firm name `firm` and a link to the source article `source_url`, and events missing either are not exposed. Firm level only, with no individual analyst names.

Cost **0.02 cr per call** · refresh: daily 23:00 UTC · docs: https://drillr.ai/docs/api/analyst-ratings

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 1) |
| `from` |  | string (date) |
| `to` |  | string (date) |
| `limit` |  | integer, default `50`, max 500 |
| `page` |  | integer, default `1` |

Example: `GET /api/v2/analyst-ratings?ticker=NVDA&from=2026-07-01&to=2026-07-31`

## Executives

Executive roster and annual compensation (US only)

### `GET /api/v2/executives` — Get self-parsed executive profiles

Returns a company's executive roster: name, position, whether currently serving, and the filing that evidences the position, one row per person per position; a person who has held several positions in turn has several rows. Start and end dates are not provided: `start_date` / `end_date` are always null (the columns stay in the contract and will be populated once 10-K Part III / 8-K Item 5.02 evidence is onboarded). Position information only, with no personal attributes such as gender or birth year.

Cost **0.02 cr per call** · refresh: weekdays 12:00 UTC; historical backfill every 30m while incomplete · docs: https://drillr.ai/docs/api/executives

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 1) |
| `is_current` |  | boolean |

Example: `GET /api/v2/executives?ticker=AAPL`

### `GET /api/v2/executive-compensation` — Get self-parsed executive compensation

Returns executives' annual compensation: salary, bonus, stock and option awards, other compensation and the total, one row per executive per compensation year, taken from the Summary Compensation Table (SCT) of the DEF 14A; the amount columns map one-to-one onto the statutory SCT columns and are all as-disclosed values in USD, neither split nor converted.

Cost **0.02 cr per call** · refresh: weekdays 12:00 UTC; historical backfill every 30m while incomplete · docs: https://drillr.ai/docs/api/executive-compensation

| param | required | type / values |
|---|---|---|
| `ticker` | yes | csv of string (max 1) |

Example: `GET /api/v2/executive-compensation?ticker=AAPL`

