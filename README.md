# drillr-skill

The agent skill for [drillr](https://drillr.ai), a financial data and research API for
the US, China and Japan. `SKILL.md` routes MCP installation to the official guide
and teaches research workflows over MCP or the REST API. REST uses an API key.

Any runtime that reads [Agent Skills](https://agentskills.io) can use it. Nothing to build.

## Install drillr MCP

To install or connect drillr MCP, read the [official installation guide](https://drillr.ai/developer/mcp-install.md).
Paste this into the app where you want to use drillr:

```text
Please connect drillr MCP in this app using this installation guide: https://drillr.ai/developer/mcp-install.md. Walk me through sign-in and verify the connection.
```

The guide covers setup, browser OAuth sign-in, and verification for your app.
Installing this skill is optional for connecting the MCP server.

## Install the skill

```bash
npx skills add Little-Grebe-Inc/drillr-skill          # skills CLI: Claude Code, Codex, Cursor, Copilot, Gemini CLI, OpenClaw …
/plugin marketplace add Little-Grebe-Inc/drillr-skill  # Claude Code; then /plugin install drillr@drillr-skill
hermes skills tap add Little-Grebe-Inc/drillr-skill    # Hermes Agent
git clone https://github.com/Little-Grebe-Inc/drillr-skill ~/.claude/skills/drillr   # by hand
```

The Claude plugin bundles the `drillr-data` MCP connection. After installation,
use the official guide to complete sign-in and verify the connection in Claude Code.

Validate or try a local checkout with Claude Code:

```sh
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate .claude-plugin/marketplace.json --strict
claude --plugin-dir .
```

The repository supports direct installation. Listing in Claude's public community
marketplace requires a separate [submission and review](https://platform.claude.com/plugins/submit).

## What drillr has

Built from primary sources: filings from SEC EDGAR, cninfo and EDINET parsed in house,
plus what companies publish on the web (IR pages, earnings calls, news) and drillr's own
estimates. Every reported figure links back to the document it came from. Coverage is
US, China and Japan unless a row says otherwise.

| Group | Data | Endpoints | Coverage |
|---|---|---|---|
| **Company** | Ticker resolution from any name, code, ISIN, CIK or CUSIP; natural-language company discovery with a match reason; company profile (exchange, industry, listing date, website, headcount) | `tickers`, `company-discovery`, `company-profile` | US CN JP (discovery also HK KR) |
| **Filings** | Filing index with form type, date and official link; full-text search inside filings in English, Chinese and Japanese, returning the passage as filed with section, form and date | `filings`, `filing-search` | US CN JP |
| **Financials** | Income statement, balance sheet and cash flow as reported under each market's standard, annual and quarterly, each figure with a derivation tree back to filed values; precomputed valuation, margin, return, growth, leverage and liquidity metrics | `income-statements`, `balance-sheets`, `cash-flow-statements`, `financial-metrics-snapshot` | US CN JP |
| **Earnings** | Earnings calendar with EPS and revenue estimates and actuals; structured earnings-call summaries (highlights, guidance, risks, segments, Q&A) | `earnings-calendar`, `earnings-call-summary` | US JP |
| **Prices** | Daily, weekly and monthly OHLC history (unadjusted) and latest close | `prices-historical`, `prices-snapshot` | US |
| **Ownership** | Insider holdings and transactions from Forms 3 / 4 / 5; institutional quarterly holdings from 13F-HR, by security or by investor | `insider-trades`, `institutional-holdings` | US |
| **Events** | A typed corporate-event timeline, plus type-specific views: equity and debt financings, M&A and agreements, executive and director changes, dividends / buybacks / splits, 13D/G stake changes — every row linked to its filing | `events`, `events-financings`, `events-deals`, `events-executive-changes`, `events-corporate-actions`, `events-ownership` | US |
| **Executives** | Executive roster with status and filing provenance; annual compensation from DEF 14A | `executives`, `executive-compensation` | US |
| **Analyst** | Individual rating and price-target changes with their source; consensus distribution with mean / high / low target | `analyst-ratings`, `analyst-consensus` | US |
| **Signal** | Conclusions drawn by drillr, each with its evidence: industry inflections synthesized across companies' earnings calls; concrete enterprise AI applications disclosed on calls; cross-source news storylines, events and attributed claims | `industry-inflections`, `enterprise-ai-adoption`, `news-search` | US (news: US CN JP + macro) |

Freshness: filings, ownership and events within minutes of the filing; calls and news within
minutes to hours; statements and analyst data daily. Pricing: one credit wallet across REST and
MCP; 0.02 cr per structured call, 0.1 per filing search, 1 per signal call, 3 per discovery;
80 free credits on sign-up. Details: <https://drillr.ai/docs/api> · <https://drillr.ai/docs/provenance> · <https://drillr.ai/pricing>.

## Two ways in

| Channel | Address | Auth | Extra |
|---|---|---|---|
| REST, Public Data API v2 | `https://gateway.drillr.ai/api/v2` · [OpenAPI](https://gateway.drillr.ai/api/v2/openapi.json) | `X-API-KEY` | the 29 endpoints above |
| MCP server `drillr-data` | `https://gateway.drillr.ai/mcp/data` | browser OAuth (API key for non-OAuth clients) | 10 tools incl. `run_sql` over the core tables (adds HK and KR listings) and `filing_search` with as-reported facts — see [drillr.ai/docs/mcp](https://drillr.ai/docs/mcp) and [drillr-mcp-server](https://github.com/Little-Grebe-Inc/drillr-mcp-server) |

## What's inside

```
drillr-skill/
├── SKILL.md                          # the skill: onboarding, conventions, the 29 endpoints, workflows, MCP pointer
├── reference/
│   ├── rest-endpoints.md             # every endpoint: params, enums, credits, refresh, doc link (generated)
│   └── mcp-supplement.md             # MCP tools, core SQL tables, ticker conventions, alt-data catalog
├── scripts/gen-reference.py          # regenerates reference/rest-endpoints.md from the live OpenAPI contract
├── examples/                         # MCP client configs (Claude Code OAuth; OpenClaw and Hermes with key) + onboarding prompts
├── .claude-plugin/plugin.json        # Claude plugin metadata
├── .claude-plugin/marketplace.json   # lets the repo act as a Claude Code plugin marketplace
├── .mcp.json                        # connects Claude to Drillr with browser OAuth
├── CHANGELOG.md
└── LICENSE (MIT)
```

Keys: <https://drillr.ai/account/api-keys> · Docs: <https://drillr.ai/docs> · Issues: <https://github.com/Little-Grebe-Inc/drillr-skill/issues>
