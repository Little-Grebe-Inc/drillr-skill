---
name: drillr
description: Financial research data for agents from drillr — read-only SQL over 90+ standardized tables (statements, ratios, prices, earnings, insider and institutional ownership, analyst ratings, 24 alt-data categories), paragraph-cited search across company filings (SEC 10-K/10-Q/8-K/20-F, Japan EDINET, HKEX, China A-share reports), semantic news and event search, and natural-language company discovery. Covers US, Japan, Hong Kong and China A-shares with fundamentals back to the 1980s. Use whenever the user asks about a stock, company fundamentals, valuation, earnings, filings, insider or fund holdings, sector or supply-chain screens, market news, or AI-value-chain data (chips, compute pricing, data centers, LLM pricing). Handles onboarding — browser sign-in for MCP clients, or an API key for relayed chats — then connects the drillr MCP server or REST API.
version: 2.0.0
license: MIT
homepage: https://drillr.ai
repository: https://github.com/Little-Grebe-Inc/drillr-skill
metadata:
  openclaw:
    homepage: https://drillr.ai
    emoji: "📈"
---

# drillr — Financial research data for agents

drillr exposes one hosted data backend through two equivalent channels:

- **MCP** (Streamable HTTP): `https://gateway.drillr.ai/mcp/data` — 9 tools, browser sign-in, no key to copy. Preferred for any MCP-capable client.
- **REST**: `https://gateway.drillr.ai/api/v2` — 29 resource endpoints (statements, filings, events, ownership…) with a public OpenAPI 3.1 contract at `/api/v2/openapi.json`; plus `/api/v1/data/<tool>` mirrors of the 9 MCP tools. Needs an API key.

Same data, same credit wallet. Every row derived from a disclosure links to the source filing.

## Coverage in one glance

| Dataset | Markets | Notes |
|---|---|---|
| Financial statements, company snapshot, price history | US, JP, HK, CN | back to the 1980s; `financial_statements`, `company_snapshot`, `price_volume_history` |
| Company filings, paragraph-level semantic search | US (EDGAR), JP (EDINET), HK (HKEX), CN (A-share) | 10-K / 10-Q / 8-K / 20-F / 6-K / S-1 / DEF 14A and local equivalents |
| Earnings calls (AI-structured summaries) and calendar | US, JP | |
| Analyst ratings and consensus, insider trades, 13F/13D/G, executives, 8-K events, extended hours | US only | |
| News, market events, attributed claims (storylines) | four markets + macro, geopolitics, commodities, crypto | |
| Alt-data, 24 categories | global | energy & power, data centers, chip specs/sales, foundry & trade, compute pricing, AI models & benchmarks, AI companies, LLM token pricing, OpenRouter usage, app rankings, web traffic, patents, papers, government contracts, trade flows, macro, social |

Ticker formats: US bare (`AAPL`), Japan `.T` (`6758.T`), Hong Kong five digits `.HK` (`00700.HK`), A-shares `.SH`/`.SZ` (`600519.SH`), indices `^GSPC`, FX `EURUSD`, crypto `BTCUSD`. Quote tickers containing `.` or `^` in SQL.

Out of scope: private companies, on-chain metrics, options chains, order books, tick data, order placement, drillr's own price forecasts.

---

## Step 1 — Detect the deployment context

One question decides the onboarding path:

> Can your MCP client open a browser for the user, and is the user sitting at it?

- **Path A — MCP client with browser OAuth** (Claude Code, Codex, Cursor, VS Code, Claude Desktop, Windsurf, most agent runtimes on the user's own machine): no key. Go to Step 2A.
- **Path B — no browser hand-off** (the user talks to you through Telegram / WhatsApp / Slack / web chat, you run on a remote host, or your runtime only speaks HTTP): API key. Go to Step 2B.

When unsure, ask:

> Quick setup question: are you at the machine I'm running on, with a browser I can open for sign-in — or are you talking to me through a chat app while I run somewhere else?

---

## Step 2A — Connect over MCP (browser sign-in)

Use the client's own MCP command. Server name `drillr-data`, URL `https://gateway.drillr.ai/mcp/data`, transport Streamable HTTP, auth browser OAuth. Tell the user the two steps that are theirs: the browser **Allow** click, and one restart (clients load MCP tools at startup).

```bash
# Claude Code
claude mcp add --scope user --transport http drillr-data https://gateway.drillr.ai/mcp/data
# then restart, run /mcp, pick drillr-data → Authenticate

# Codex
codex mcp add drillr-data --url https://gateway.drillr.ai/mcp/data
```

Cursor (`.cursor/mcp.json`) / other JSON-config clients:

```json
{ "mcpServers": { "drillr-data": { "type": "http", "url": "https://gateway.drillr.ai/mcp/data" } } }
```

VS Code uses `.vscode/mcp.json` with a top-level `servers` key. Claude Desktop: Settings → Connectors → Add custom connector → paste the URL → Connect. Per-client detail: <https://drillr.ai/developer/mcp-install.md>.

The consent screen shows **drillr Data**. A drillr account is created on first sign-in (Google sign-in is quickest). Never add an `Authorization` header to an entry that uses OAuth.

## Step 2B — Connect with an API key (relayed chat or REST)

**Tell the user (verbatim):**

> To use drillr I need an API key. From any browser (your phone is fine):
>
> 1. Open https://drillr.ai/account/api-keys
> 2. Sign in — Google sign-in is quickest
> 3. Create a key (scope **external**), name it e.g. "my-agent", copy the `drl_…` string
> 4. Paste it here. It is shown only once; you can delete your message after I confirm it works.

**Persist it** (mode 0600), then verify:

```bash
mkdir -p ~/.config/drillr && umask 077
printf '{ "api_key": "%s" }\n' "$KEY" > ~/.config/drillr/config.json
curl -sS -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $KEY" \
  "https://gateway.drillr.ai/api/v2/tickers?query=Apple%20Inc.&market=US"   # expect 200
```

**Confirm masked:** `Stored drl_xxxxxxxx_…e9f2 — you can delete your message now.`

Then either point an MCP client at `/mcp/data` with `"headers": { "Authorization": "Bearer drl_…" }` (Hermes, OpenClaw, and other non-OAuth clients — see `examples/`), or call REST directly with `Authorization: Bearer drl_…` (or `X-API-KEY: drl_…`).

Rules: never echo the full key; never write it anywhere except `~/.config/drillr/config.json` or the user's own secret store; on storage failure report the exact error instead of holding the key in memory.

---

## Step 3 — Use the tools

Recommended order: resolve the ticker → check schemas → structured data via SQL → narrative via filing search → discovery and news as needed.

| Tool | Use it for | Not for | Cost |
|---|---|---|---|
| `ticker_lookup` | name / brand / substring → canonical ticker(s), first when the user names a company | discovery by description | free |
| `list_tables` | discover alt-data tables by category (1–5 categories per call) | fundamentals tables (reach those directly) | free |
| `get_table_schema` | columns and types of any of the 90+ tables; call before treating zero rows as absence | | free |
| `fiscal_utility` | fiscal year/quarter ↔ calendar month for a ticker (Apple ends Sep, Nvidia Jan) | JP/HK sparse, CN not configured | free |
| `run_sql` | read-only PostgreSQL SELECT over fundamentals, prices, ownership, analyst, events, alt-data | filing narrative, company discovery, news | 0.1 cr |
| `sec_report_list` | which filings exist for a ticker (types, dates, periods) | filing content | 0.1 cr |
| `sec_report_search` | paragraph-level semantic search inside filings: risk factors, MD&A, guidance, segments, related parties, dilution, properties | consolidated numbers (use SQL) | 0.1 cr |
| `news_search` | news, market events, attributed claims grouped into storylines; filter by query / theme / ticker / since / until | filing text | 0.2 cr |
| `company_search` | natural-language discovery: business model, supply chain, peers, themes; `market` ∈ us/jp/hk/cn | numeric screens (use SQL on `company_snapshot`) | 3–5 cr, usage-based |

REST equivalents: `POST /api/v1/data/run_sql`, `POST …/sec_report_search`, `GET …/sec_report_list`, `POST …/company_search`, `POST …/ticker_lookup`, `POST …/news_search`, `GET …/list_tables`, `GET …/get_table_schema`, `GET …/fiscal_utility`. For scripts and pipelines prefer the typed v2 resources (`/api/v2/income-statements?ticker=AAPL&period=FY&limit=4` etc.); see <https://drillr.ai/docs/api>.

### SQL rules (`run_sql`)

- SELECT only. No CTEs (`WITH`) — use subqueries. No `pg_*` / `information_schema`.
- Date columns are TEXT: compare as strings (`period_end >= '2024-01'`); no `::date` casts or `INTERVAL`.
- No `ROUND(float8, int)`; use `CAST(x AS DECIMAL(10,2))`.
- Structured tables need a ticker filter (`WHERE ticker IN ('AAPL','MSFT')`); alt-data tables don't. Exclude preferred stock in screens with `AND ticker NOT LIKE '%-%'`.
- Rows come back positional (`columns` + `rows`); zip them.

### Filing-search playbook

Time-specific questions: set `period_start`/`period_end` first. Broad questions: one or two unfiltered searches to see what exists, then narrow. High-value phrases: `"Risk Factors"`, `"Segment Information"`, `"Outlook"` / `"Guidance"`, `"Market Risk"`, `"Properties"`, `"Shareholders' Equity"` (dilution, SBC, buybacks), `"Critical Accounting Policies"`, `"Stock Split"`.

---

## Typical workflows

**Quick lookup** — "What's Nvidia's gross margin trend?"
`ticker_lookup("Nvidia")` → `run_sql` on `financial_statements` (`fiscal_period='FY'`, last 5 `period_end`) → answer with the periods spelled out.

**Filing deep-dive** — "What does Apple say about China risk?"
`sec_report_list("AAPL")` → `sec_report_search({ticker:"AAPL", query:"China regulatory and demand risk", filing_types:["10-K"], period_start:"2024-01"})` → quote passages with form and date.

**Sector scan** — "Japanese lithography suppliers"
`company_search({query:"semiconductor lithography equipment makers", market:["jp"]})` → `run_sql` on `company_snapshot` for the tickers returned → rank.

**Daily briefing** — for a watchlist of tickers
`news_search({ticker:[…], since:"<24h-ago ISO>", search_type:"events", order_by:"event_time"})` → for anything material, `sec_report_search` or `run_sql` for context → short headline-plus-two-lines per item with source links.

**Alt-data** — "How has H100 rental pricing moved?"
`list_tables({categories:["Compute Pricing"]})` → `get_table_schema(<table>)` → `run_sql` (no ticker filter needed).

---

## Errors, limits, credits

| HTTP | `error.code` | Do |
|---|---|---|
| 400 | `invalid_request` / `bad_request` | fix the parameter or SQL and retry; don't ask the user |
| 401 | `unauthenticated` / `key_invalid` / `key_revoked` / `key_expired` | OAuth: re-authenticate in the client. Key: re-read `~/.config/drillr/config.json` or `DRILLR_API_KEY` first; only then ask for a new key |
| 402 | `insufficient_credits` | tell the user; top-ups and plans at https://drillr.ai/pricing |
| 403 | `forbidden` | key lacks `external` scope; user must create one with that scope |
| 404 | `not_found` | ticker out of coverage or dataset not available; check `get_table_schema` coverage notes before concluding |
| 429 | `rate_limited` / `concurrency_limit_exceeded` | sleep `retry_after_seconds`, retry |
| 502 / 503 / 504 | upstream / unavailable / timeout | retry once after 2–3 s, then surface |

Rate limit 30 requests/min per key on `/api/v1` and MCP, 100/min on `/api/v2`. Failed calls are not billed. REST responses carry `_credits` (`charged`, `method`, `balance_after`); MCP does not — check https://drillr.ai/account/api-keys. Free tier: 80 credits; Plus $29/300 cr; Ultra $99/1,500 cr.

Never tell the user to "check their configuration" — diagnose first.

## Reference

- API reference: <https://drillr.ai/docs/api> · OpenAPI: <https://gateway.drillr.ai/api/v2/openapi.json>
- MCP install (per client): <https://drillr.ai/developer/mcp-install.md>
- Tool reference: <https://github.com/Little-Grebe-Inc/drillr-mcp-server/blob/main/docs/tools.md>
- Keys: <https://drillr.ai/account/api-keys> · Pricing: <https://drillr.ai/pricing>
- Issues: <https://github.com/Little-Grebe-Inc/drillr-skill/issues>

Tracks drillr MCP server v2.2 and Public Data API v2 (2026-09).
