# Changelog

All notable changes to this skill are tracked here. The skill version
tracks the Drillr External API version it was written against.

## [2.1.0] — 2026-09-13

REST-first rewrite, aligned with drillr.ai/docs.

### Changed
- The skill now documents the Public Data API v2 (29 endpoints in 10 groups) as its primary surface: conventions, per-endpoint one-liners with coverage, credits, and six workflows written as REST calls. Every endpoint links to `drillr.ai/docs/api/<endpoint>`.
- MCP is a pointer, not a manual: connect `drillr-data`, let the server describe its 10 tools, and use `reference/mcp-supplement.md` for what MCP adds (`run_sql`, fact-level `filing_search`). This removes the tool-name drift that hit 2.0.0 (`sec_report_*` → `filing_*`, `fiscal_utility` gone, `industry_inflections` and `ai_adoption` new).
- Positioning follows the docs: financial data and research API for US, China and Japan, built from primary filings, every figure traceable. Alternative data is no longer a headline; the 9 public categories are listed in the MCP supplement as a secondary SQL capability.
- Description field rewritten around the REST data groups.

### Added
- `reference/rest-endpoints.md`, generated from the OpenAPI contract by `scripts/gen-reference.py`.
- `reference/mcp-supplement.md`: MCP tool index, the 17 core SQL tables, ticker conventions, alt-data catalog verified against the public server.

## [2.0.0] — 2026-09-13

Rewritten against the current server. Breaking for anyone who scripted the v1 tool names.

### Changed
- MCP endpoint is `https://gateway.drillr.ai/mcp/data` (server name `drillr-data`); `/mcp` and the v1 tool set (`search`, `signals`, `article_*`, `watchlist_*`) are gone.
- Browser OAuth is the default for MCP clients (Path A); the API-key flow is kept for relayed chats and non-OAuth runtimes (Path B).
- Nine data tools documented with when-to-use / not-for / cost: `ticker_lookup`, `list_tables`, `get_table_schema`, `fiscal_utility`, `run_sql`, `sec_report_list`, `sec_report_search`, `news_search`, `company_search`.
- REST: points at the typed Public Data API v2 (`/api/v2`, OpenAPI at `/api/v2/openapi.json`) for scripts, with the `/api/v1/data/*` tool mirrors listed.
- Coverage table: US, Japan, Hong Kong, China A-shares; US-only datasets called out; 24 alt-data categories.
- Key URL is `https://drillr.ai/account/api-keys`.

### Removed
- `drillr-cli` instructions (the CLI is being reworked; the npm package predates the current API).

### Added
- `.claude-plugin/marketplace.json` so the repo installs as a Claude Code plugin marketplace and directories flag it "marketplace ready".
- Example configs renamed to `drillr-data`; Claude Code example is OAuth-only.

## [1.0.0] — 2026-04-23

Initial release. Complete rewrite of the earlier repository contents.

### What's covered

- **Three channels**: MCP (Streamable HTTP), REST, CLI — all accept
  the same `drl_*` API key
- **Dual onboarding paths**:
  - Path A (indirect): IM / web-chat / remote-host agents; user
    pastes key into chat, agent persists to
    `~/.config/drillr/config.json` (mode `0600`)
  - Path B (direct): co-located terminal; three equivalent sub-paths
    (MCP via Claude Code, `drillr-cli`, REST + env var)
- **Nine capabilities**: `search`, `signals`, `article_list`,
  `article_get`, `watchlist_list`, `watchlist_create`, `watchlist_add`,
  `watchlist_remove`, `watchlist_delete`
- **Frontmatter compatible with both** Anthropic Agent Skills and the
  clawhub / openclaw skill format (same `SKILL.md`, different consumers)
- **Example MCP configs** for Claude Code, OpenClaw, Hermes
- **Copy-paste user-onboarding prompts** in
  `examples/user-onboarding-script.md`

### Deliberately not covered

- OAuth 2.1 flow for MCP (browser callback is incompatible with
  remote-host deployments; token TTL is a moving target in the
  client ecosystem)
- Helper scripts wrapping the API — the earlier revision shipped a
  Python wrapper, but that coupling is what rots first when the API
  evolves. Agents should call MCP / REST / CLI directly.

### API version

Tracks Drillr External API **v1** (2026-04). Breaking changes will
ship under `/api/v2/*` alongside `/api/v1/*`; this skill will bump
its minor version when v1 gains non-breaking additions, and bump
major when switching to v2.
