# AGENTS.md — fastweb-ai-hack

FastwebAI Hackathon 2026, **Moncler track**. We build a pipeline that reads multilingual store
closing emails, turns them into SKU-linked demand signals, corrects the short-term forecast and
proposes stock actions as decision cards for a human. Rule: **AI reads, code counts, humans decide.**

State: docs, a synthetic test dataset and the PLT-01 scaffold (`backend/` FastAPI, `web/` React+Vite).
Repo "today" = **Thu 2026-10-22**.

## Read this, skip the rest

The repo has ~3,150 tracked files (~200 MB), almost all data. Don't list, grep or open them in bulk.

| Need | Read | Don't read |
|---|---|---|
| What we build, modules, data contracts, math | `docs/RFC-001-piattaforma.md` (Italian; read the § you need) | `docs/project-design.md` §3–§8, `docs/drafts/fastweb.md` (superseded) |
| Who owns which paths, task order, dependencies | `docs/PLAN.md` | — |
| What is done, in progress, ready to pick up | GitHub issues (`gh issue list`), see "Task workflow" | — |
| Brief, scoring, pitfalls | `docs/findings.md` | `docs/sources/**` (raw verbatim sources; `findings.md` already digests them) |
| Dataset layout, formats, traps, time rules, scenarios | `generated/README.md` (§2 map, §3 parsing, §4 no look-ahead, §5 dev/hold-out) | — |
| Store list, ids, tz, currency, language | `generated/sources/erp/master_data/stores.csv` | — |

When you need a data file, find it via the table in `generated/README.md` §2, then inspect a sample
(`head -n 20`, one `.eml`, `python -c` on a single CSV). Never `cat` whole CSVs or read every email
of a store. Partitioned folders (`sales/daily_store_sku/`, `inventory/store_stock_daily/`,
`forecast/sku_store_weekly/`) share one schema: read one file.

## Commands

Requires `uv` and Node >= 22. Run from the repo root.

- `make setup`: install backend (`backend/.venv`) and web deps from the lockfiles.
- `make dev`: backend :8000, web :5173 (proxies `/api`), dataset mock systems :8088.
- `make check`: ruff, pytest, oxlint, tsc. Must pass before every PR (CI runs it too).
- `make fmt`: auto-fix Python lint and formatting.
- Add deps with `cd backend && uv add <pkg>` or `cd web && npm install <pkg>`; never hand-merge lockfiles.

Secrets: copy `.env.example` to `.env` (gitignored). Never print, log or commit `FASTWEB_API_KEY`.
Stay inside your lane's paths (`docs/PLAN.md` §1–§2).

## Task workflow (GitHub issues)

GitHub issues are the **only** task board. One issue per task, title `<TASK-ID> (<lane>): <summary>`,
label `lane:A`…`lane:E`. Open + no assignee = ready. Open + assignee = in progress. Label `blocked` +
"Blocked by" relationship = waiting. Closed = done. Spec of each task: `docs/PLAN.md` §4.

Follow these steps in order, every time. Do not skip or reorder them.

1. **Pick.** `gh issue list --state open --label lane:<X> --json number,title,assignees,labels`.
   Take only an issue that has **no assignee** and **no `blocked` label**. Never work on an issue
   assigned to someone else, even if it looks stale: ask them in the team chat.
2. **Claim before any code.** `gh issue edit <N> --add-assignee @me`, then re-read the issue
   (`gh issue view <N> --json assignees`). If anyone else is assigned too, the one who claimed first
   keeps it: unassign yourself and pick another issue.
3. **Branch** from up-to-date `main`, named `<TASK-ID>-<slug>` (e.g. `PLT-04-orchestrator`), exactly
   the task ID from the issue title.
4. **Draft PR at once.** Make a first commit (even empty: `git commit --allow-empty -m "<TASK-ID>: start"`),
   push, and open a **draft** PR: `gh pr create --draft --title "<TASK-ID>: <summary>"
   --body "Closes #<N>"`. Then push small commits often: every push is a checkpoint others can see.
5. **Finish.** `make check` passes.
6. **Ready.** `gh pr ready <PR>`, then squash-merge; `Closes #<N>` closes the issue.
7. **Unblock.** After merge, for every issue blocked by yours: if all its blockers are closed,
   remove the `blocked` label.

Creating and splitting issues:

- New task, blocker or dependency discovered: open an issue (or comment on the existing one). Set
  dependencies with GitHub's "Blocked by" relationship and add the `blocked` label.
- A task too large for one PR: split it into **sub-issues** of the parent issue (e.g. `(pure)` and
  `module` parts). Each sub-issue follows the steps above; close the parent when all are closed.
- Before opening an issue, search for duplicates (`gh issue list --state all --search "<TASK-ID>"`).
  If one exists, use it; if you created a duplicate, close yours as "not planned" with
  `Duplicate of #<N>`.

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
- Python env: `backend/.venv/` (uv). Mock agents server: `make mocks` (runs
  `generator/systems/mock_agents/server.py` with that env; run it, don't import or read it).
- Docs in English. Don't edit files under `docs/sources/`.
