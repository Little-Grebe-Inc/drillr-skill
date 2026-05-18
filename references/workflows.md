# Drillr Workflows — Multi-Tool Templates

This file is loaded only when the user asks for a research workflow
that spans 3+ tool calls. For single-tool guidance, see `SKILL.md`.

All examples assume the dispatcher is invoked as
`python scripts/drillr.py call <tool> ...`. Snippets are pseudo-code
focusing on the decision flow, not literal shell.

---

## 1. "Tell me everything about <ticker>" — company snapshot

User: *"What's the story with NVDA right now?"*

1. **Resolve** — if user said a name instead of ticker, `company_search`
2. **Recent activity** — `signal_list?tickers=NVDA&limit=10` to find
   high-score events from the last 7-14 days
3. **Latest filing** — `sec_report_list?ticker=NVDA&filing_types=10-K,10-Q&limit=2`
4. **Filing color** — `sec_report_search` with `query: "key business
   updates"` constrained to the most recent quarter
5. **Numbers** — `run_sql` for the last 4-8 quarters of revenue, gross
   margin, EPS, and a valuation snapshot
6. **Synthesize** — 5 sections:
   - One-paragraph summary
   - Recent signals (3-5 bullets)
   - Latest filing highlights (3-5 bullets, quoted)
   - Quarterly numbers (small table)
   - Watch items (open questions, upcoming catalysts)

**Don't dump JSON to the user.** Convert SQL rows to a named table.
Quote filing paragraphs with citation.

---

## 2. Peer comparison

User: *"How does AMD stack up against NVDA on margins and growth?"*

1. `sec_report_search` per ticker for the metrics requested (e.g.
   `query: "gross margin operating margin"`) — for standardized
   financials this is usually the most reliable path; the SQL
   catalog may not surface fundamentals.
2. If `list_tables` does surface a fundamentals table, use the SQL
   three-piece flow (`list_tables` → `get_table_schema` → `run_sql`)
   to pull a longer time series in one shot.
3. `sec_report_search` again for `query: "competitive positioning"`
   on each ticker's most recent 10-Q for qualitative color.
4. Format as side-by-side table; flag deltas > 200 bps or > 10% growth
   diff as "notable".

**Pitfall:** if the two tickers have different fiscal calendars (NVDA
ends Jan, most peers end Dec), call `fiscal_utility` first so you're
comparing comparable periods.

---

## 3. "What just happened?" — event-driven investigation

User: *"Why did NVDA pop 4% today?"*

1. `signal_list?tickers=NVDA&from_date=<24h-ago iso>&limit=20` — newest
   first
2. Sort by `score`; the trigger is usually score ≥ 3
3. If trigger is a filing (`event_types` includes `earnings`, `8K`,
   `13F`), drill in:
   - `sec_report_list?ticker=NVDA&limit=1` to find the filing
   - `sec_report_search` for the topic alluded to in the signal
4. If trigger is news, the signal `summary` + `trigger_sources` is
   usually enough
5. If no clear trigger, check sector-wide signals
   (`signal_list?sector=information_technology`) — might be a sector
   rotation, not a single-name event

---

## 4. Sector / theme scan

User: *"Anything interesting in lithium / data centers / China tech
this week?"*

1. **Discover candidates** — `company_search` with the theme as
   natural-language query
2. **Filter** — if `company_search` results need further structured
   filtering (country, market cap, listing exchange), discover a
   company-metadata table via `list_tables` and use the SQL
   three-piece flow. Skip this step if `company_search` already
   returned what you need.
3. **Activity scan** — `signal_list` with the candidate tickers as
   `tickers` filter (chunk into batches of ≤ 20)
4. **Highlight** — top 5 signals by score; for each, one-sentence
   thesis + source citation

---

## 5. Filing-driven deep dive

User: *"Read NVDA's latest 10-Q and tell me what they said about
data-center demand."*

1. `sec_report_list?ticker=NVDA&filing_types=10-Q&limit=1` — confirm
   period
2. `sec_report_search` with `{ticker:"NVDA", query:"data center
   demand and visibility", period_start:"<that quarter>",
   period_end:"<that quarter>", filing_types:["10-Q"]}`
3. Cluster the returned paragraphs by sub-theme (orders, channel mix,
   geography, capacity)
4. Quote selectively; cite form + period + a section name (e.g. "MD&A
   — Operating Segment Results")

---

## 6. Watchlist morning brief

User: *"Run my morning brief on AAPL, MSFT, NVDA, GOOGL."*

1. `signal_list?tickers=AAPL,MSFT,NVDA,GOOGL&from_date=<12h-ago>&limit=40`
2. For each ticker with ≥1 score-3+ signal, pull one-line context with
   a follow-up `sec_report_search` only if the signal references a
   filing
3. For a 1-line price + change snapshot per ticker: discover the
   price table via `list_tables` (only once per session — cache the
   name), then `run_sql` projecting close + the date column ordered
   DESC LIMIT 2 per ticker. (Don't hard-code the table name; the
   SQL schema is dynamic.)
4. Format: per-ticker block of 3 lines:
   - Headline price action
   - Top signal (if any)
   - Watch item / open question (if any)

Skip tickers with no signals and flat price action — don't pad.

---

## 7. Alt-data exploration (AI value chain)

User: *"Show me what alt-data you have on AI inference pricing."*

1. `list_tables?categories=LLM Token Pricing,Compute,AI Models`
2. Pick the relevant tables from the response
3. `get_table_schema` on each candidate to see what columns exist
4. `run_sql` to pull the slice the user asked about

Surface the **table description** to the user alongside results so
they know provenance.

---

## Anti-patterns

- **Don't `SELECT *`** from large fact tables — project columns
  explicitly. Wide selects on time-series / event fact tables can
  time out and burn your context budget.
- **Don't hard-code SQL table names** from memory or from this
  file. The catalog is dynamic — always discover via `list_tables`
  + `get_table_schema` (see `references/sql_schemas.md`).
- **Don't make N+1 calls** when one query with `WHERE ticker IN (...)`
  works.
- **Don't paste raw JSON** to the user. Reshape into prose, tables, or
  bullet lists.
- **Don't fabricate filing quotes.** If `sec_report_search` returns
  nothing matching, say so — don't paraphrase from memory.
- **Don't ignore `_credits.balance_after`.** If it dips below ~10% of
  what it was when the session started, warn the user before pressing
  on with expensive follow-ups (`sec_report_search` × N).
