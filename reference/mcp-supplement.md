# MCP supplement — what the drillr MCP server adds over REST

Server `drillr-data` · `https://gateway.drillr.ai/mcp/data` · Streamable HTTP · browser OAuth
(API-key header for clients without OAuth). Setup: https://drillr.ai/developer/mcp-install.md.
Each tool has a page at `https://drillr.ai/docs/mcp/<tool>` with parameters, limits and error shapes;
the server's `tools/list` carries the same descriptions, so treat this file as an index.

| Group | Tool | Purpose | Cost |
|---|---|---|---|
| Company | `ticker_lookup` | name / brand / substring → canonical symbols, historical names included (`market` us/cn/jp) | free |
| | `company_search` | natural-language discovery; `market` us/cn/jp/hk/kr; all matches returned; daily cap 20 / 100 / 500 | 3–5 cr |
| Filings | `filing_list` | which filings are indexed for a ticker (fiscal period, type, date); `filing_types` allowlist | 0.1 cr |
| | `filing_search` | one company's filings → **Facts** (as-reported values with metric, period, XBRL concept, accession) and **Passages**; `period_start/end` are calendar `YYYY-MM-DD`, `fiscal_period` FY/Q1–Q4/H/9M, `as_of` cutoff, `top_k` ≤ 30 | 0.1 cr |
| Datasets | `list_tables` | alt-data category index, or the tables under up to 5 categories | free |
| | `get_table_schema` | one table's columns, types and usage note (required filters, coverage) — read before SQL | free |
| | `run_sql` | one read-only SELECT; 100 rows Free/Plus, 500 Ultra; 10 s; 5 in flight | 0.1 cr |
| Signal | `industry_inflections` | `keyword`, `ticker` (≤10, US), `impact_companies` for per-company effects | 1 cr |
| | `ai_adoption` | `ticker` / `company_name` / `application_name` / `since` | 1 cr |
| | `news_search` | `query` / `theme` / `ticker` / `since` / `until`, `search_type` all·events·claims, `order_by` | 0.2 cr |

## `run_sql` — core tables

Coverage: US, Japan, Hong Kong, China A-shares and Korea for `financial_statements`, `company_snapshot`,
`price_volume_history`; specialized tables can be narrower — `get_table_schema` states each table's coverage.

| Domain | Tables |
|---|---|
| Market | `price_volume_history` (OHLCV; filter `ticker` + `time_frame`), `index_price`, `equity_extended_rt` (pre/after/overnight) |
| Fundamentals | `financial_statements` (GAAP income / balance / cash flow; `fiscal_period` FY or Q1–Q4), `company_snapshot` (ratios, per-share, growth, ~170 columns) |
| Earnings | `earning_call_summary`, `earning_call_calendar` |
| Analyst | `analyst_ratings`, `analyst_ratings_consensus` |
| Ownership | `insider_and_institution_activities` |
| 8-K events | `executive_change`, `company_deal_events`, `debt_issuance`, `securities_offering` |
| Executives | `executive_profile`, `executive_compensation` |

Rules: SELECT only, no CTE (use subqueries); period columns are TEXT `YYYY-MM` (compare as strings, no `::date`);
filter structured tables by ticker (`ticker NOT LIKE '%-%'` drops preferred shares in screens); quote symbols with
`.` or `^` (`'6758.T'`, `'^GSPC'`). Ticker forms: US bare, `.SH`/`.SZ`, `.T`, `.HK` (five digits), `.KS`/`.KQ`,
indices `^GSPC` `^N225`, FX `EURUSD`, crypto `BTCUSD`, commodities `CLUSD`.

## Alt-data via `list_tables` (secondary; MCP only, no REST endpoints)

9 categories, 65 tables, mostly the AI supply chain and macro. Discover with `list_tables(categories=[…])`,
inspect with `get_table_schema`, query with `run_sql` (no ticker filter needed).

| Category | Tables |
|---|---|
| Energy & Power (3) | `eia_generators`, `eia_retail_prices`, `eia_regional_hourly` |
| Data Centers (5) | `epochai_data_centers`, `epochai_data_center_timelines`, `epochai_gpu_clusters`, `epochai_dc_cooling_towers`, `epochai_dc_chillers` |
| Semiconductors (12) | `epochai_chip_types`, `epochai_ml_hardware`, `epochai_chip_organizations`, `epochai_chip_sales_*` (3), `epochai_chip_owners_*` (3), `tsmc_revenue`, `twcustoms_trade`, `computeprices_gpus_dim` |
| Compute Pricing (6) | `computeprices_gpu_offer_daily`, `computeprices_gpu_offers`, `computeprices_providers_dim`, `skypilot_ondemand_price`, `skypilot_spot_price`, `skypilot_instance_dim` |
| Model Development (11) | `epochai_models`, `epochai_benchmark_scores`, `epochai_benchmark_runs`, `epochai_ai_companies` (+ revenue / usage / staff / funding / compute-spend reports), `epochai_polling`, `arena_leaderboard` |
| Inference Economics (5) | `litellm_price_history`, `litellm_models_dim`, `computeprices_llm_prices`, `computeprices_llm_price_daily`, `computeprices_llms_dim` |
| Macro & Trade (6) | `comtrade_country`, `comtrade_hs_code`, `census_import_export`, `fred_series`, `fred_observations`, `fred_macro_daily` |
| Prediction Markets (12) | `polymarket_events` / `_markets` / `_outcomes` / `_trades` / `_daily` / `_volume_daily` / `_holders_daily`, `kalshi_events` / `_markets` / `_trades` / `_daily` / `_volume_daily` |
| Critical Minerals (5) | `mineral_deposit`, `mineral_deposit_commodity`, `mineral_deposit_operator`, `mineral_country_supply`, `mineral_critical_snapshot` |

Catalog verified against the public server on 2026-09-13.
