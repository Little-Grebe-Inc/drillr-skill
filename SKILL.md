---
name: drillr
description: Drillr financial-research data for US and Japan public equities. Provides eight tools — standardized financial statements and ratios via SQL over 90+ tables, paragraph-level SEC filing semantic search (10-K / 10-Q / 20-F / 6-K / S-1 / DEF 14A), company / ticker resolution, a live cross-asset signal feed, fiscal-period utilities, and AI value-chain alt-data. Invoke whenever the user asks about stocks, tickers, financial statements, earnings, SEC filings, insider trading, institutional ownership, market signals, or sector / industry research. Requires a user-specific API key obtainable at https://drillr.ai/developer/keys.
version: 2.0.0
license: MIT
homepage: https://drillr.ai
repository: https://github.com/Little-Grebe-Inc/drillr-skill
metadata:
  openclaw:
    homepage: https://drillr.ai
    emoji: "📈"
  hermes:
    namespace: drillr
    category: research
  lobehub:
    identifier: drillr
    category: finance
---

# Drillr — Financial Research for Agents

Drillr is a financial-research data backend for AI agents. This skill
teaches you how to call its eight tools to answer questions about US
and Japan public equities — fundamentals, SEC filings, earnings,
insider activity, signals, and AI value-chain alt-data.

All access is via a single REST endpoint, wrapped by a Python
dispatcher shipped with this skill at `scripts/drillr.py`. **Do not
write raw curl commands** — invoke the dispatcher instead. It handles
authentication, error mapping, and credit accounting in one place.

---

## Setup — verify or onboard the API key

Before any tool call, run a probe. The dispatcher reads the key from
the single source of truth: `~/.drillr/config.json`.

```bash
python scripts/drillr.py probe
```

**Possible outcomes:**

| stderr first line     | Exit | What to do                                                                |
| --------------------- | ---- | ------------------------------------------------------------------------- |
| (success — JSON on stdout) | 0  | Key is valid. Proceed.                                                  |
| `NO_KEY: ...`         | 2    | Run the onboarding flow below.                                            |
| `INVALID_KEY: ...`    | 3    | Existing key was revoked / expired. Re-run onboarding to refresh.         |
| `RATE_LIMIT: ...`     | 4    | Transient. Wait, then retry; do not bother the user.                      |
| `NETWORK: ...`        | 1    | Gateway unreachable. Surface the error to the user.                       |

### Onboarding flow (when probe returns NO_KEY or INVALID_KEY)

Detect your deployment context first — it changes the wording you use,
not the steps:

- **Co-located**: you're running in a terminal the user is also typing
  into (Claude Code, OpenClaw, Hermes CLI). You can suggest commands;
  the user pastes the key back.
- **Relayed**: you reach the user via Telegram / Slack / Discord / a
  chat UI, with no shared shell. The user opens a browser on their
  own device and pastes the key back to you.

Either way, the steps are:

1. Ask the user to open <https://drillr.ai/developer/keys> in any
   browser (phone works). Google sign-in is the fastest path.
2. Tell them to click **Create API key**, name it (e.g. `my-agent`),
   and copy the key string. It is shown only once.
3. When they paste it back, store it:

   ```bash
   python scripts/drillr.py setup-key <the_key_they_pasted>
   ```

4. Re-run `probe` to confirm the key works.
5. **Confirm with a masked key, AND explicitly tell the user to
   delete the message containing the full key.** This is a required
   step, not optional. Example wording:

   > Stored `dgr_live...e9f2`, balance 10,083 cr. **Please delete
   > your message with the full key now** — it's been persisted in
   > my session log and you don't want it sitting in chat history.

   Never echo the full key back to the user. Never include it in any
   summary, recap, or follow-up.

If `setup-key` fails (permission error on `~/.drillr/`), surface the
exact error to the user; never silently hold the key in memory.

---

## Tool overview — what to call when

All tools are invoked the same way:

```bash
python <abs_path>/scripts/drillr.py call <tool> [--json '<body>' | --query '<qs>']
```

- **POST tools** take `--json '<body>'` (object).
- **GET tools** take `--query 'k=v&k=v'` (preferred) or `--json
  '<object>'` (auto-converted to query string). Don't pass a non-object
  to `--json` for GET tools — it errors out.
- **Always pass the absolute path** to `scripts/drillr.py` — many hosts
  (OpenClaw, Hermes) sandbox shell execs and reject `cd <dir> && python …`
  or other compound commands. Look up the skill's install path
  (`$SKILL_DIR` if provided, else `~/.openclaw/workspace/skills/drillr/`
  or `~/.openclaw/skills/drillr/` or `~/.hermes/skills/drillr/` or
  `~/.claude/skills/drillr/`) and use it directly.

| Tool                | Method | Use when the user asks about…                                                                                              |
| ------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------- |
| `company_search`    | POST   | "Find me NVDA / Apple / semiconductor companies / AI infrastructure peers" — resolve a name to a ticker; surface peers     |
| `run_sql`           | POST   | Numeric fundamentals — financials, ratios, prices, earnings, insider, ownership. 90+ standardized tables                   |
| `list_tables`       | GET    | Discover available alt-data tables in a category (`Twitter`, `AI Models`, `Compute`, etc.)                                 |
| `get_table_schema`  | GET    | Inspect columns / types of a specific table before writing SQL                                                             |
| `sec_report_list`   | GET    | List filings (10-K / 10-Q / 20-F / 6-K / S-1 / DEF 14A) for a ticker and date range                                        |
| `sec_report_search` | POST   | Paragraph-level semantic search inside SEC filings — risk factors, MD&A, segment notes, etc.                               |
| `signal_list`       | GET    | "What's moving in the market today / this week?" — curated cross-asset event feed with importance scoring                  |
| `fiscal_utility`    | GET    | Map fiscal periods to calendar dates for companies with non-calendar fiscal years (e.g. NVDA's FY ends in January)         |

> **Always invoke via `python scripts/drillr.py call <tool>`**, not
> raw HTTP. The dispatcher already knows the method and URL.

For exact parameters per tool, read `references/tools.md` (loaded
only when needed). For the 90+ SQL table catalog, read
`references/sql_schemas.md`. For multi-tool workflow templates, read
`references/workflows.md`.

---

## Decision tree — picking the right tool

A user question is rarely a 1:1 mapping to a tool. Common patterns:

### Numbers about a known ticker

"AAPL gross margin last 4 quarters" / "MSFT operating cash flow trend":

1. If the ticker is implied not explicit ("Apple" / "the chip giant"),
   first `company_search` to resolve.
2. For **time-series / numeric data potentially in the SQL layer**
   (prices, alt-data, anything tabular), use the SQL three-piece flow
   — `list_tables` → `get_table_schema` → `run_sql`. Do not write
   SQL against a table name from memory; the catalog is dynamic.
   See `references/sql_schemas.md`.
3. For **standardized financials** (income statement, ratios,
   balance-sheet items, EPS, margin %): if `list_tables` doesn't
   surface a relevant table, **route to `sec_report_search`** and
   extract the number from the latest 10-Q / 10-K paragraph text.
   This is the canonical fallback — don't apologize for it.
4. **Treat `get_table_schema` returning `columns: []` as the table
   not existing** (current gateway behavior: 200 + empty instead of
   404). Move on; don't `run_sql` against it.
5. `run_sql` only accepts `SELECT` — the gateway rejects anything else
   with `400 invalid_request`.

### "What did the filing say about X" → `sec_report_search`

"How does NVDA describe its export-license risk?" / "What guidance did
TSLA give for FY26 in the latest 10-Q?":

1. `sec_report_search` with `{query, ticker}` returns paragraph-level
   matches with citation metadata. Quote the text and cite the filing
   period and form type.

### Whole-filing browsing → `sec_report_list`

"What did NVDA file recently?" — `sec_report_list?ticker=NVDA&limit=10`.

### Markets / news / signals → `signal_list`

"Anything moving in semis today?" / "What's the most important news
about NVDA this week?":

1. `signal_list?tickers=NVDA&from_date=<iso>&limit=20`
2. For each notable signal, optionally drill into a fuller report with
   `sec_report_search` (if the trigger is a filing) or `run_sql` (if
   the trigger is a price move).

### Sector / theme discovery → `company_search`

"AI infrastructure leaders" / "lithium miners with US exposure" —
`company_search` accepts natural-language descriptions, not just
tickers. Returns candidates with `match_reason`.

### Fiscal-period gymnastics → `fiscal_utility`

When the user says "Q3" but the company's fiscal year doesn't line up
with calendar quarters (NVDA's FY ends January, AAPL's ends
September), use `fiscal_utility` before constructing date filters in
`run_sql`.

---

## Common workflows

### Quick lookup (price / time-series)

User: *"What's NVDA's last close?"*

1. `list_tables` to find the table holding daily prices (look for
   categories / table summaries that mention prices, OHLCV, or
   market data).
2. `get_table_schema` on the candidate to learn the column names
   (the schema is dynamic — don't assume `period_end` / `close` /
   `time_frame` ahead of time).
3. `run_sql` projecting just the columns you need, ordered DESC by
   the date column, `LIMIT 1`.
4. Return one number + the as-of date.

### Quick lookup (fundamentals)

User: *"What was AAPL's gross margin last quarter?"*

1. Run `sec_report_search` on the latest 10-Q:
   `{"ticker":"AAPL","query":"gross margin","top_k":5}`
2. Extract the % from the returned paragraph; cite the form type
   and fiscal period.
3. Don't try SQL first — standardized financial tables aren't
   reliably present in `run_sql` today.

### Quarterly comparison (fundamentals)

User: *"Compare AMD and NVDA gross margin last 4 quarters."*

1. Run `sec_report_search` per ticker for the most recent 4 quarters'
   filings; extract the gross-margin row from each.
2. Build a comparison table from the extracted numbers.
3. Cite each cell with its source filing period.

### Filing-driven research

User: *"Summarize NVDA's latest 10-Q risk factors."*

1. `sec_report_list?ticker=NVDA&form_type=10-Q&limit=1` to confirm the
   most recent quarter.
2. `sec_report_search` with `{query: "risk factors", ticker: "NVDA"}`
   constrained to that filing.
3. Cluster the returned paragraphs by theme; quote selectively; cite
   the form type and fiscal period.

### Morning market scan

User: *"Brief me on what moved in semis overnight."*

1. `signal_list?sector=information_technology&from_date=<8h-ago iso>&limit=30`
2. Filter for high-score signals (`score >= 3`).
3. For top 3-5, return headline + 1-sentence implication.

More workflow templates: `references/workflows.md`.

---

## Output and citation discipline

- **Numbers**: always state the unit (USD millions, percentage points,
  share count). Always state the as-of date / fiscal period.
- **Filing quotes**: cite form type + fiscal period + ticker (e.g.
  "NVDA 10-Q FQ3 2026 — Item 1A Risk Factors").
- **Signals**: when summarizing, include the source name(s) from
  `trigger_sources` so the user can verify.
- **SQL output**: never present raw column tuples — convert to a
  named table or prose. The user does not want to read JSON.

---

## Out of scope

Drillr does not cover:

- Private / unlisted companies (US + Japan public listings only)
- On-chain crypto metrics (TVL, wallet flow, holders). It has CEX
  prices for BTC/ETH/SOL, not chain data.
- Options chains, real-time order book, intraday tick data
- Retail brokerage actions (placing orders, managing positions)
- Drillr does not produce its own price forecasts — surface analyst
  consensus, not opinion

If the user asks for any of the above, say so directly and suggest the
nearest in-scope substitute (e.g. "I don't have options chains, but I
can pull recent implied-vol commentary from analyst transcripts via
`sec_report_search`").

---

## Runtime caveats — host-specific gotchas

These are things that bit real users; SKILL.md notes them up-front so
the agent doesn't burn turns rediscovering them.

### Exec sandbox: use absolute paths, no compound commands

OpenClaw, Hermes, and some Claude Code configurations sandbox shell
execution and **reject `cd … && python …` or any inline compound
command** with `complex interpreter invocation detected; refusing to
run without script preflight validation`.

Always invoke with the absolute path to the skill's `scripts/drillr.py`:

```bash
# good
python /home/admin/.openclaw/workspace/skills/drillr/scripts/drillr.py probe

# bad — sandbox will reject
cd ~/.openclaw/skills/drillr && python scripts/drillr.py probe
```

If you can't find the install path, list the typical candidates and
test `os.path.exists` on each. Common locations:

- `~/.openclaw/workspace/skills/drillr/` (OpenClaw agent-installed)
- `~/.openclaw/skills/drillr/` (OpenClaw user-global)
- `~/.hermes/skills/drillr/`
- `~/.claude/skills/drillr/`

### Python 3.6 environments

Some target Linux hosts (Alibaba Cloud, RHEL/CentOS family) ship
Python 3.6.8 as the default. The dispatcher (`scripts/drillr.py`) is
3.6-compatible. **If you write a helper script** to batch calls or
parse output:

- Don't use `subprocess.run(..., capture_output=True)` — that's 3.7+.
  Use `stdout=subprocess.PIPE, stderr=subprocess.PIPE`.
- Don't use walrus `:=`, `dict | dict` merge, or `from __future__
  import annotations` features.

### `get_table_schema` returns `columns: []` for missing tables

Today the gateway returns `200` with `data.columns = []` for tables
that don't exist, instead of `404`. **If `columns` is empty, treat
the table as non-existent** — do not proceed to `run_sql` against it.
See `references/sql_schemas.md` for the workflow.

This is a known gateway behavior that may change; when it returns a
proper error, this note can go away.

---

## Error handling

The dispatcher maps HTTP status to structured stderr + exit codes.
React per code:

| Exit | stderr label   | Recover by…                                                                |
| ---- | -------------- | -------------------------------------------------------------------------- |
| 0    | (none)         | Parse stdout JSON, continue                                                |
| 1    | `USAGE` / `NETWORK` / `PARSE` | Tool was misused or gateway unreachable. Fix and retry once. |
| 2    | `NO_KEY`       | Run onboarding flow above                                                  |
| 3    | `INVALID_KEY`  | Key revoked / expired — re-run onboarding to refresh                       |
| 4    | `RATE_LIMIT`   | Wait ~30s and retry. Do not pester the user. Pace ≤ 0.5 req/s              |
| 5    | `API_ERROR`    | Read the JSON body printed under the label; usually a parameter problem.   |

**On a 401 (`INVALID_KEY`), the most common cause is a revoked key,
not a typo.** Diagnose by reading `~/.drillr/config.json` and the
exit-code label *before* asking the user.

---

## Reference files

Loaded only when the task requires them — `progressive disclosure`:

| File                         | When to read                                                         |
| ---------------------------- | -------------------------------------------------------------------- |
| `references/tools.md`        | Need exact parameter shape, response schema, or credit cost          |
| `references/sql_schemas.md`  | Writing `run_sql` and need to discover the right table / column      |
| `references/workflows.md`    | User asks for a research workflow that spans 3+ tool calls           |

---

## Notes for runtime authors

- The dispatcher uses Python 3 stdlib only (`urllib`, `json`, `ssl`).
  No `pip install` required.
- Gateway base URL defaults to `https://gateway.drillr.ai`. Override
  for staging / local with the `DRILLR_GATEWAY_URL` env var.
- Key storage path is `~/.drillr/config.json` (mode 0600). This is
  the **single source of truth** — the dispatcher does not check
  environment variables, keychain, or anywhere else. If you need to
  rotate, run `setup-key` again or delete the file.

---

## Reference links

- Drillr web: <https://drillr.ai>
- API keys: <https://drillr.ai/developer/keys>
- Developer docs: <https://drillr.ai/developer/docs>
- Gateway: `https://gateway.drillr.ai`
- MCP endpoint (for hosts that don't support skills): `https://gateway.drillr.ai/mcp/data`

Tracks Drillr External API **v1** (2026-05). Breaking changes ship as
`/api/v2/*` alongside `/api/v1/*`.
