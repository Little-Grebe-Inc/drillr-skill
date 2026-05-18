# Changelog

All notable changes to this skill are tracked here. The skill version
tracks the Drillr External API version it was written against.

## [2.0.0] — 2026-05-18

Major rewrite. Skill is now positioned as the **primary entry point**
for SKILL.md-compatible agent runtimes (OpenClaw, Hermes, Claude
Code, etc.); the MCP server [drillr-mcp-server](https://github.com/Little-Grebe-Inc/drillr-mcp-server)
is the fallback for runtimes that don't support skills.

### Why this changed

- Skills load progressively (only when relevant) — MCP servers are
  always-on context. For users with an Anthropic-Skills-compatible
  host, a skill is the lighter-weight entry point.
- The previous v1.0.0 skill described the older "product API"
  (`search` / `signals` / `articles` / `watchlists`); current Drillr
  exposes eight finer-grained data tools (`run_sql`,
  `sec_report_search`, etc.) which the v2 SKILL.md now targets
  directly.

### What's new

- **Helper script** — `scripts/drillr.py`: stdlib-only Python
  dispatcher that wraps the 8 REST data endpoints. Agents invoke it
  rather than writing raw curl, which avoids 0→1 prompt-engineering
  of headers and bodies on every call.
- **Single source of truth for credentials** — `~/.drillr/config.json`
  (mode `0600`). No fallback to env vars or alternate paths; if it's
  not there, the dispatcher exits with `NO_KEY` and the onboarding
  flow in SKILL.md kicks in.
- **Progressive disclosure** — SKILL.md stays short (~250 lines);
  details live in `references/tools.md`, `references/sql_schemas.md`,
  `references/workflows.md`, loaded only when the task needs them.
- **Multi-platform metadata** — frontmatter carries
  `metadata.openclaw.*`, `metadata.hermes.*`, and `metadata.lobehub.*`
  namespaces so a single repo publishes across marketplaces.
- **Structured exit codes** — `0` ok, `2` `NO_KEY`, `3` `INVALID_KEY`,
  `4` `RATE_LIMIT`, `5` `API_ERROR`, `1` other. Agents react per code
  rather than parsing error strings.

### What's gone

- Old `examples/` directory (MCP config templates per host) — removed.
  Runtimes that need the MCP-server flow now go to
  [drillr-mcp-server](https://github.com/Little-Grebe-Inc/drillr-mcp-server)
  directly.
- Path A / Path B (indirect / direct) explicit branching — collapsed
  into one onboarding flow with deployment-context detection notes,
  since the action steps are identical.

### Breaking changes vs v1.0.0

- Capability surface is completely different (`run_sql` /
  `sec_report_search` / `company_search` / `signal_list` /
  `list_tables` / `get_table_schema` / `fiscal_utility` /
  `sec_report_list`, vs old `search` / `signals` / `articles` /
  `watchlists`). Agents written against v1 will need new prompts.
- Key storage path moved from `~/.config/drillr/config.json` (XDG) to
  `~/.drillr/config.json`. Re-run setup once.

### API version

Tracks Drillr External API **v1** (2026-05). The data-tools surface
(`/api/v1/data/*`) is the canonical path; the older `/api/v1/search`
/ `/api/v1/articles` etc. routes still exist for backward compat but
this skill no longer targets them.

---

## [1.0.0] — 2026-04-23

Initial release. Documented MCP / REST / CLI access to drillr's
product-level API (`search` / `signals` / `articles` / `watchlists`).
Dual onboarding paths for co-located vs relayed deployments. No
helper scripts shipped — agents called the API directly.

Superseded by 2.0.0.
