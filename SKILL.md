---
name: drillr
description: Financial data and research API for US, China and Japan equities, built by drillr from primary filings (SEC EDGAR, cninfo, EDINET); every figure links to the passage it was filed in. 29 REST endpoints: ticker resolution, natural-language company discovery, filing lists and full-text filing search (EN/ZH/JA), the three statements as reported plus valuation metrics, earnings calendar and structured call summaries, US insider trades and 13F holdings, corporate-event timelines (financings, deals, executive changes, corporate actions, 13D/G stakes), executive rosters and pay, analyst ratings and consensus, and research signals (industry inflections, enterprise AI adoption, news storylines). Use whenever the user asks about a listed company's fundamentals, filings, earnings, ownership, events or analysts, wants companies by description, or follows market news. Handles API-key onboarding, then calls gateway.drillr.ai/api/v2; points MCP-capable clients at the MCP server.
version: 2.1.0
license: MIT
homepage: https://drillr.ai
repository: https://github.com/Little-Grebe-Inc/drillr-skill
metadata:
  openclaw:
    homepage: https://drillr.ai
    emoji: "📈"
---

# drillr — financial data and research API

drillr is a financial data and research API for the US, China and Japan. Beyond the
financial statements it searches the full text of filings, finds companies from a
natural-language description, and publishes research signals extracted from filings,
news and earnings calls. The data is built by drillr from primary sources — filings
taken from SEC EDGAR, cninfo and EDINET and parsed in house — and every reported
figure links back to the document it came from.

Docs: <https://drillr.ai/docs> · API reference: <https://drillr.ai/docs/api> ·
OpenAPI: <https://gateway.drillr.ai/api/v2/openapi.json> · Pricing: <https://drillr.ai/pricing>

This skill works over **REST**, so it runs in any runtime that can make an HTTP request.
If your client speaks MCP, see [MCP instead of REST](#mcp-instead-of-rest) at the end:
same data, browser sign-in, plus SQL and fact search.

## Step 1 — Get a key (once)

Tell the user:

> To use drillr I need an API key. From any browser:
> 1. Open https://drillr.ai/account/api-keys and sign in (Google is quickest; 80 free credits, no card).
> 2. Create a key, scope **external**, name it e.g. "my-agent", copy the `drl_…` string.
> 3. Paste it here — it is shown only once. Delete your message after I confirm it works.

Store it where your runtime keeps secrets (`~/.config/drillr/config.json` with mode 0600,
or the `DRILLR_API_KEY` environment variable), never in chat logs or files you commit. Verify:

```bash
curl -sS -H "X-API-KEY: $DRILLR_API_KEY" \
  "https://gateway.drillr.ai/api/v2/tickers?query=Apple%20Inc.&market=US"
# → {"data":[{"ticker":"AAPL","market":"US","name":"Apple Inc.","exchange":"XNAS",...}]}
```

Confirm to the user with the key masked (`drl_xxxxxxxx…e9f2`). On 401 re-read your stored
key before asking for a new one. `Authorization: Bearer drl_…` is accepted as well.

## Step 2 — Know the conventions

- Base URL `https://gateway.drillr.ai/api/v2`; GET with query parameters, except `POST /news-search` (JSON body).
- **One ticker identifies both company and market**: `AAPL`, `600519.SH` / `300750.SZ`, `6758.T`. Use `/tickers` to turn a name, code, ISIN, CIK or CUSIP into it; `/company-discovery` when you only have a description.
- Dates are `YYYY-MM-DD`, ranges inclusive. Paging only where `limit` / `page` are listed (pages start at 1; a short page is the last). No numeric filters: fetch rows and filter yourself.
- Responses are `{"data": [rows]}`. Rows derived from a disclosure carry `filing_url`, `accession_number` or a source link. Cite them.
- 100 requests per minute per key. Errors are `{"error", "message"}` with `bad_request`, `unauthenticated`, `insufficient_credits` (402), `not_found` (ticker out of coverage), `rate_limit_exceeded` (429 with `retry_after_seconds`, not billed), `internal_error`, `service_unavailable`.
- Credits: 0.02 per structured call (24 endpoints), 0.1 per filing-search, 1 per signal call, 3 per company-discovery. Failed calls are not billed.

## Step 3 — The data (29 endpoints)

One line each. Parameters, response fields and worked examples live on
`https://drillr.ai/docs/api/<endpoint>`; the whole contract with credits and refresh
cadence is in `reference/rest-endpoints.md`.

| Group | Endpoint | What you get | Coverage |
|---|---|---|---|
| Company | `GET /tickers` | name / code / ISIN / CIK / CUSIP → canonical ticker, or list a whole market | US CN JP |
| | `GET /company-discovery` | natural-language description → tickers with a match reason (3 cr) | US CN JP HK KR |
| | `GET /company-profile` | name, exchange, industry, listing date, website, headcount | US CN JP |
| Filings | `GET /filings` | a company's filings with form type, filing date and the official document link | US CN JP |
| | `GET /filing-search` | full-text search inside one company's filings; original passages with section, form and date (0.1 cr) | US CN JP |
| Signal | `GET /industry-inflections` | industry changes synthesized from many earnings calls: mechanism, scope, degree, per-company impact (1 cr) | US |
| | `GET /enterprise-ai-adoption` | concrete AI applications disclosed on earnings calls: workflow, stage, value type, evidence (1 cr) | US |
| | `POST /news-search` | storylines, events and attributed claims across sources, with links to the articles (1 cr) | US CN JP + macro |
| Financials | `GET /income-statements` `GET /balance-sheets` `GET /cash-flow-statements` | as reported under each market's standard, FY or Q1–Q4, with a derivation tree back to filed values | US CN JP |
| | `GET /financial-metrics-snapshot` | market cap, multiples, margins, returns, growth, leverage, liquidity | US CN JP |
| Prices | `GET /prices-historical` · `GET /prices-snapshot` | daily / weekly / monthly OHLC, unadjusted · latest close | US |
| Earnings | `GET /earnings-calendar` | announcement dates with EPS and revenue estimates and actuals (`from`, `to` required) | US JP |
| | `GET /earnings-call-summary` | highlights, guidance, risks, segments, Q&A, structured — not the transcript | US JP |
| Ownership | `GET /insider-trades` | Forms 3 / 4 / 5 holdings and transactions, parsed from the filings | US |
| | `GET /institutional-holdings` | 13F-HR by security (who holds it) or by `investor_cik` (what they hold) | US |
| Events | `GET /events` | one typed timeline: financings, deals, executive changes, corporate actions, ownership | US |
| | `GET /events-financings` `…-deals` `…-executive-changes` `…-corporate-actions` `…-ownership` | the same events with type-specific fields (terms, counterparties, roles, 13D/G stakes) | US |
| Analyst | `GET /analyst-consensus` · `GET /analyst-ratings` | rating distribution with mean / high / low target · individual rating and target changes with source | US |
| Executives | `GET /executives` · `GET /executive-compensation` | roster with status and filing provenance · annual pay from DEF 14A | US |

Freshness: filings, ownership and events within minutes of the filing; calls and news within
minutes to hours; statements and analyst data daily. Each endpoint states its own cadence as
`x-refresh` in the OpenAPI document.

## Step 4 — Workflows

**Quick fundamentals.** "How has Apple's gross margin moved?"
`/tickers?query=Apple` → `/income-statements?ticker=AAPL&period=FY&limit=5` → compute from
`revenue` and `gross_profit`; quote `report_period` and `filing_url`.

**Find a fact in a filing.** "What does NVDA say about supply commitments?"
`/filings?ticker=NVDA` to see what exists → `/filing-search?ticker=NVDA&query=supply+commitments&form_type=10-K&from=2025-01&to=2025-12`
→ answer with the passage, its section, form and date. Query in the filing's own language for CN and JP.

**Screen by description.** "Japanese factory-automation makers with net cash"
`/company-discovery?query=factory automation and industrial robot makers&market=JP` → for each
ticker `/financial-metrics-snapshot` and `/balance-sheets` → filter and rank locally.

**Ownership check.** "Who bought and sold ACME this quarter?"
`/insider-trades?ticker=ACME&from=…&to=…&transaction_type=buy,sell` plus
`/institutional-holdings?ticker=ACME&report_period=…`; for stake changes, `/events-ownership?ticker=ACME`.

**Daily briefing** for a watchlist.
`POST /news-search {"ticker":[…],"since":"<24h ago>","search_type":"events","order_by":"event_time"}` →
for anything material, `/events?ticker=…` or `/filing-search` for context → one headline, two lines and a link per item.

**Signal scan.** "Which industry shifts are under-noticed?"
`/industry-inflections?keyword=…` (or `ticker=` for one company's exposure); `company_impacts` gives
direction, degree and stage per company. `/enterprise-ai-adoption?ticker=…&since=…` shows what a company actually deploys.

## MCP instead of REST

If your client supports MCP (Claude Code, Codex, Cursor, VS Code, Claude Desktop), connect the
server instead of using a key. Same data and credits, browser sign-in.

- Server `drillr-data`, URL `https://gateway.drillr.ai/mcp/data`, Streamable HTTP, browser OAuth.
- Setup per client: <https://drillr.ai/developer/mcp-install.md>. Tool pages: <https://drillr.ai/docs/mcp>.
- The server describes its own 10 tools, so nothing needs to be memorised here. Two things it has that REST does not: `run_sql` (read-only SQL over the core financial, price, earnings, ownership, analyst, event and executive tables, including HK and KR listings) and `filing_search` returning structured as-reported facts alongside passages. Details in `reference/mcp-supplement.md`.
- Clients without OAuth can pass `"headers": {"Authorization": "Bearer drl_…"}` on the same URL (see `examples/`).

## Reference

- `reference/rest-endpoints.md` — every endpoint with parameters, enums, credits, refresh and doc link. Generated from the OpenAPI contract; regenerate with `scripts/gen-reference.py`.
- `reference/mcp-supplement.md` — MCP tools, core SQL tables, ticker conventions.
- Provenance and freshness: <https://drillr.ai/docs/provenance> · Benchmark: <https://drillr.ai/drillr-benchmark> · Issues: <https://github.com/Little-Grebe-Inc/drillr-skill/issues>
