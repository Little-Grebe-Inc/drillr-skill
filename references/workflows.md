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

1. `run_sql` once with `WHERE ticker IN ('AMD','NVDA')` on
   `profitability_ratios` for last 4-8 quarters
2. `run_sql` for `growth_metrics` similarly
3. `sec_report_search` for each: `query: "competitive positioning"`,
   pick the most recent 10-Q each
4. Format as side-by-side table; flag deltas > 200 bps or > 10% growth
   diff as "notable"

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
2. **Filter** — `run_sql` on `company_profile` if you need to apply
   structured filters (country, market cap, listing exchange)
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
3. `run_sql` for a 1-line price + change snapshot per ticker (yesterday
   close vs prior close from `price_volume_history`)
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

- **Don't `SELECT *`** from large fact tables — projects columns
  explicitly. Wide selects on `price_volume_history` /
  `insider_trades` can time out.
- **Don't make N+1 calls** when one query with `WHERE ticker IN (...)`
  works.
- **Don't paste raw JSON** to the user. Reshape into prose, tables, or
  bullet lists.
- **Don't fabricate filing quotes.** If `sec_report_search` returns
  nothing matching, say so — don't paraphrase from memory.
- **Don't ignore `_credits.balance_after`.** If it dips below ~10% of
  what it was when the session started, warn the user before pressing
  on with expensive follow-ups (`sec_report_search` × N).
