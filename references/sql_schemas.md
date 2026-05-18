# Drillr SQL Layer — Discovery Guide

Drillr's `run_sql` + `list_tables` + `get_table_schema` are a **dynamic
three-piece toolkit**: the agent is expected to discover the available
schema at runtime, not memorize a catalog. This file teaches the
discovery workflow and SQL constraints — **deliberately no specific
table or column names are listed**, because the live schema evolves
and any names baked into this file would rot.

This file is loaded only when you're about to write `run_sql`. For
tool-call syntax, see `references/tools.md`.

---

## Golden rule

**Discover, don't guess.** Never invent a table name from memory.
Always:

1. `list_tables` to enumerate what's available (by category).
2. `get_table_schema` on a candidate to learn its columns + types.
3. `run_sql` once you've confirmed the table exists and you know
   the column names you need.

If you skip step 1 or step 2, you'll burn turns chasing
`relation "<x>" does not exist` errors.

---

## Discovery workflow

```bash
# 1. enumerate tables in one or more categories
python <skill_dir>/scripts/drillr.py call list_tables \
  --query "categories=<Category1>,<Category2>"
# → response: data[].tables[].{name, summary}
#   pick the table that matches what you need

# 2. confirm the table exists + see real columns
python <skill_dir>/scripts/drillr.py call get_table_schema \
  --query "table_name=<the_one_you_picked>"
# → response: data.columns[].{column_name, data_type, comment}
# ⚠️  if columns is [] (empty array), treat the table as NOT existing.
#    Today the gateway returns 200 with empty columns instead of 404
#    for unknown tables. Don't proceed to run_sql.

# 3. query
python <skill_dir>/scripts/drillr.py call run_sql \
  --json '{"sql":"SELECT col1, col2 FROM <table> WHERE ticker=... LIMIT N"}'
```

If `list_tables` returns no useful candidates, or the category
you'd need doesn't exist, the data may not be in the SQL layer
at all. Move to the **fallback strategy** below.

---

## When SQL doesn't have what the user asked for

The SQL layer's coverage evolves. If a metric the user wants isn't
discoverable via `list_tables` (or the candidate table you find has
`columns: []`), **don't keep guessing variant names**. Switch to
`sec_report_search` and extract the figure from the latest 10-Q /
10-K filing text:

```bash
python <skill_dir>/scripts/drillr.py call sec_report_search \
  --json '{"ticker":"<TICKER>","query":"<metric described in plain english>","top_k":5}'
```

10-Q / 10-K filings contain the structured financial tables as
text. Vector search returns paragraph-level snippets with citation
metadata; pull the numbers from the matched text and cite the form
type + fiscal period in your final answer.

---

## SQL hard rules

These are gateway-enforced — don't waste a call probing them:

- **`SELECT` only.** `INSERT` / `UPDATE` / `DROP` / DDL return
  `400 invalid_request`.
- **No `information_schema` / `pg_*`.** System-catalog access is
  blocked with `400 invalid_request "Access to information_schema /
  pg_* system catalogs is not allowed"`. Use `list_tables` /
  `get_table_schema` instead — that's the supported discovery path.
- **No multi-statement queries.** One statement per call.
- **Joins, CTEs, window functions, aggregates** all supported.
- **Currency is USD** unless the column you're reading carries an
  explicit currency code.

---

## Practical SQL hygiene

- **Project columns explicitly** — never `SELECT *` against a wide
  fact table. Returned payloads compete with your context budget,
  and wide selects can time out on large tables.
- **Filter by `ticker` (uppercase)** — that's the standard primary
  key for equity-keyed tables.
- **For time-series tables, filter by the date / timestamp column**
  to bound the row count. Confirm the exact column name via
  `get_table_schema`.
- **One query, not N.** If you need data for 5 tickers, use
  `WHERE ticker IN ('A','B','C','D','E')`, not 5 separate calls.

---

## Anti-patterns

- ❌ Writing `SELECT ... FROM <table_name_from_memory>` without
  `get_table_schema` first.
- ❌ When a query fails with "relation does not exist", retrying
  with `<name>_v2`, `financial_<name>`, `<name>s`, etc. — those are
  guesses. If `list_tables` didn't surface the right table,
  fundamentals are probably not in SQL at all; fall back to
  `sec_report_search`.
- ❌ Apologizing to the user about "I don't have direct SQL access
  to that metric, but…" — just route to `sec_report_search` quietly
  and deliver the answer. The user wants the number, not the
  plumbing.
- ❌ Calling `information_schema.tables` or `pg_catalog.*`. Use
  `list_tables`.
