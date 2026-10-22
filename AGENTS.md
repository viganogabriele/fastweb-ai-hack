# AGENTS.md — fastweb-ai-hack

FastwebAI Hackathon 2026, **Moncler track**. We build a pipeline that reads multilingual store
closing emails, turns them into SKU-linked demand signals, corrects the short-term forecast and
proposes stock actions as decision cards for a human. Rule: **AI reads, code counts, humans decide.**

State: docs + a synthetic test dataset. No product code yet, so no build/test commands exist.
Repo "today" = **Thu 2026-10-22**.

## Read this, skip the rest

The repo has ~3,150 tracked files (~200 MB), almost all data. Don't list, grep or open them in bulk.

| Need | Read | Don't read |
|---|---|---|
| What we build, modules M0–M14, data contracts, math | `docs/project-design.md` (use its §-headings, read the section you need) | `docs/drafts/fastweb.md` (superseded) |
| Brief, scoring, pitfalls | `docs/findings.md` | `docs/sources/**` (raw verbatim sources; `findings.md` already digests them) |
| Dataset layout, formats, traps, time rules, scenarios | `generated/README.md` (§2 map, §3 parsing, §4 no look-ahead, §5 dev/hold-out) | — |
| Store list, ids, tz, currency, language | `generated/sources/erp/master_data/stores.csv` | — |

When you need a data file, find it via the table in `generated/README.md` §2, then inspect a sample
(`head -n 20`, one `.eml`, `python -c` on a single CSV). Never `cat` whole CSVs or read every email
of a store. Partitioned folders (`sales/daily_store_sku/`, `inventory/store_stock_daily/`,
`forecast/sku_store_weekly/`) share one schema: read one file.

## Hard rules (answer leakage)

- Product code, prompts, fixtures, RAG indexes and few-shot examples read **only
  `generated/sources/`**.
- **Do not open `generated/ground_truth/`, `generator/`, or any `*_notes.md` / `email_context`
  file.** They hold the hidden test answers. Exception: only when the task is explicitly eval code
  (M14, keep it in `eval/`, never imported by product code) or dataset maintenance.
- `generated/sources/` is read-only. Derived/cleaned data goes in `data/`.
- Don't re-run `generator/world.py` or any builder: it desyncs ~2,000 hand-written emails.
- No look-ahead: when simulating evening D, use only data available by D (`generated/README.md` §4).
- Tune on dev stores, report on hold-out stores (`generated/README.md` §5).

## Conventions

- Store id (`MIL01`…) is the master key. SKU = `<style_code>-<colour_code>`, SKU-size adds `-<size>`.
- ERP money is net of VAT and returns, in local currency; emails/reports often are not.
- Python env: `.venv/` (uv). Mock agents server: `.venv/bin/python generator/systems/mock_agents/server.py --port 8088`
  (run it, don't import or read it).
- Docs in English. Don't edit files under `docs/sources/`.
