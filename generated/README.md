# generated/ — how to use this dataset (read before touching anything)

Controlled synthetic world for the Moncler track (module **M0 "World simulator"** in `docs/project-design.md`).
39 stores, 18 countries, 114 style-colours / 643 SKU-sizes. Sales run from 2024-09-01 to 2026-10-21, and the store emails, POS lines and stock run from Aug to Oct 2026.
**"Today" = Thursday 2026-10-22.** All people, influencers, vendors and competitors are fictional.

```
generated/
├── README.md        ← this file
├── sources/         ← INPUT. The only thing the product may read.             (~2,870 files, 189 MB)
└── ground_truth/    ← ANSWERS. Only the eval harness (M14) may read it.         (14 MB)
generator/           ← (repo root) code + briefs that built all of the above. Contains the answers too.
```

---

## 1. Rules — if you only read one section, read this

| # | Rule | Why |
|---|---|---|
| R1 | **The product (pipeline, agents, prompts, UI) reads only `generated/sources/`.** | Everything else contains the answers. |
| R2 | **Never read `ground_truth/`, `generator/` or `generator/events.py` at runtime, and never paste them into an LLM prompt, a few-shot example, a RAG index, a fixture or a system prompt.** | `events.py`, `WORLD_BRIEF.md`, `EMAIL_SPEC.md`, `email_context/*.json` and `answer_keys/*` describe exactly what is hidden. One leak makes every metric meaningless. |
| R3 | **Only the eval harness (M14)** may open `ground_truth/`, to compare outputs against the truth. Keep that code in its own folder (e.g. `eval/`), with no imports from it into the product. | Keeps the oracle separate. |
| R4 | **`sources/` is read-only.** Don't fix, clean, rename or re-encode files in place. Put derived or cleaned data in your own folder (e.g. `data/fixtures/`, `data/cache/`). | Cleaning *is* part of the challenge; other people's tests rely on the raw files. |
| R5 | **No look-ahead.** When you simulate "the evening of day D", use only what existed by D (see §4). | Otherwise the lead-time claim ("we see it before sales do") is fake. |
| R6 | **Don't tune on everything.** Tune prompts, thresholds and vague-quantifier tables on the **dev stores** only and report metrics on the **hold-out stores** (§5). | Avoids the circularity the jury will ask about. |
| R7 | **Don't re-run `generator/world.py` or any builder** unless you're the dataset owner. The hand-written emails, reports and chats are tied to the exact numbers it produced. | One re-run with a changed parameter silently desyncs ~2,000 emails from the sales data. |
| R8 | Coding agents (Claude Code, Codex, Cursor...): give them **this file + `sources/`**. Tell them explicitly *"do not open generated/ground_truth or generator/ unless you are writing eval code"*. | Agents grep everything they can see. |

When a coding agent works on **product** code, add this to its prompt or `CLAUDE.md`:

> Data lives in `generated/sources/` (read-only). Do NOT read `generated/ground_truth/`, `generator/`, or any `*_notes.md` / `email_context` file; they are the hidden test answers. Derived data goes in `data/`.

---

## 2. What is in `sources/` and which module uses it

| Folder | What | Format quirks | Main modules |
|---|---|---|---|
| `erp/master_data/` | `stores.csv` (id, city, tz, currency, language), `styles.csv`, `sku_colour.csv`, `sku_size_ean.csv`, `price_list_FW26.csv`, `store_assortment.csv` | clean | catalog for M4 linking, M10 |
| `erp/sales/daily_store_sku/` | daily sales store×SKU, 2024-09-01 → 2026-10-21, one CSV per month | clean; **censored by stock** (no sales ≠ no demand) | M9 baseline, backtest |
| `erp/sales/pos_lines/` | receipt lines Aug–Oct 2026, with size, customer nationality, tax-free flag, payment, **returns with reason code** (DEF, SIZE...) | NYC02 Oct 6 receipts posted on Oct 7 | M5, M6, anomalies |
| `erp/kpi/store_daily_kpi.csv` | net sales, budget, receipts, visitors, conversion, UPT, ATV | MAD01 visitors = 0 on Oct 1–7 (broken counter) | M10, card |
| `erp/traffic/` | door counter daily | gaps | S3 traffic factor |
| `erp/inventory/store_stock_daily/` | end-of-day on-hand per store×SKU×**size**, Aug 1 → Oct 21 | doesn't show inter-store transfers or COU01's seasonal return | M10 checks, S7 |
| `erp/logistics/` | DC→store shipments (planned vs actual, received SKU) | MAD01 received a different SKU than ordered | M10 lead times |
| `erp/forecast/` | **event-blind statistical forecast**: SKU×store×week (one file per Monday run), store weekly value, region xlsx | levels don't reconcile; SYD01 uses northern seasonality; new products use an analog ×0.6 | M9 baseline to correct |
| `store_emails/<STORE>/*.eml` | **2,056 closing emails**, Aug 31 → Oct 21, one per open store-day + replies, forwards, corrections, duplicates, wrong-list sends, OOO, attachment-only mails | it, es, fr (+CH), de (+CH), en (UK/US/AU/SG/AE/NL/DK flavours), ja, ko, zh-CN/HK/TW; charsets ISO-2022-JP, EUC-KR, GB18030; HTML parts; CSV/XLSX/JPG attachments; local time zones in `Date:` | M1–M5 (the heart) |
| `internal_comms/` | area-manager weekly recaps, chat exports (WhatsApp, Teams JSON, KakaoTalk, LINE, WeChat), store visit reports, HQ memos, voice-of-customer | each export in its native format | M3 extra evidence, M13b |
| `reports/` | 25 reports (XLSX/PDF/PPTX/DOCX/CSV) from controlling, regions, JP/KR/CN, merch, agency, market research, tax-free operator, quality, board | **conflicting metric definitions** (FX, VAT, calendars, sell-through, LFL perimeter) + real mistakes | M7 reconciler |
| `external/` | weather (per-provider formats, °F/°C), tides, 10-day forecast, holidays ICS, events, strikes, Rome ordinance, tourism with **publication lag**, flight seats, hotels, tax-free index, trends, ~4.7k social posts (3 vendors), ~80 news items, FX, macro | schema changes mid-period, relative indices, duplicates, mixed timestamps | M8 context, S2/S4 |
| `systems/` | other departments + their agents: `warehouse/` (SAP-like DC stock, POs, ATP, quality holds), `logistics/` (tracking, customs, incidents, transfers, **lane lead-time/cost matrix**), `marketing/` (campaigns, CRM clienteling notes, waitlists, PR), `planning/` (OTB, allocation, replenishment params, S&OP minutes), `ecommerce/`, `customer_care/`, `agents/` (agent cards, OpenAPI, examples, inter-agent log), `reference/` (ID crosswalk) | different IDs per system (MIL01 / 1001 / CRM code / ship-to), SKU with or without size, EAN | M10, M13a/c |

**Mock agents server** (for M13): `.venv/bin/python generator/systems/mock_agents/server.py --port 8088`, run from the repo root.
Routes are `/<warehouse|logistics|marketing|planning>/v1/...`, specified in `sources/systems/agents/`. Every endpoint accepts `asOf=YYYY-MM-DD` to replay a past day.
Running the server is fine; importing its code into the product is not (it reads `sources/` only, but lives in `generator/`).

### Conventions
- **Store id** `MIL01`... is the master key (`erp/master_data/stores.csv`). Other systems use other codes; see `systems/reference/`.
- **SKU** = `<style_code>-<colour_code>` (e.g. `J20931A00012-999` = MAIRE black). SKU-size = `+ -<size>`. Sizes: women outerwear `00 0 1 2 3 4`, men `1–7`, knit/jersey `XS–XXL`, shoes EU, accessories `TU`.
- Staff never write codes: they write "la Maire nera", "粉色", "イルバロ", "the long black one". Colour names in 8 languages are in `generator/config.py`. Copy that list into your own code; don't import it.
- **Money:** `erp` amounts are **net of VAT/consumption tax and of returns**, in **local currency**. `net_sales_eur_bud` uses 2026 budget FX. Emails and reports often quote VAT-inclusive, gross, k€, 万 or 천원 figures.
- **Dates:** `business_date` is the store's local date. Email `Date:` headers carry the local offset. Social and logistics timestamps are mostly UTC, with exceptions.

---

## 3. Parsing tips (the traps you'll hit first)

- **.eml**: use Python `email` with `policy=email.policy.default`, then `msg.get_body(('plain','html'))`, and handle `multipart/alternative` and attachments. Don't assume UTF-8: let the library decode the declared charset.
- **Duplicates and corrections:** the same day can have 2–3 mails (duplicate send, "scusate, il fatturato era 38k non 83k", reply threads quoting the original). Dedup on content and thread, and prefer the latest correction.
- **Subject dates lie** sometimes; trust the `Date:` header and the body. Some mails cover two days (weekend recap) or are sent next morning.
- **Quoted text:** replies contain the previous mail (`>` lines, "Le … a écrit :"). Don't count the same claim twice.
- **Numbers in mail:** "16,1k", "1억 6,912만", "12.3万", "CHF 24'620.–", "EUR 8.465" (Dutch thousands dot), "5,340万円 税込". Never feed them to the math without normalisation.
- **Reports:** read the definitions/footnotes before comparing numbers; three different "sell-through"s exist.
- **External:** tourism statistics stop at Jul/Aug 2026 (publication lag). Trends are relative per file. The social vendor changed schema on 2026-09-15.

---

## 4. Time discipline (no look-ahead)

To replay "the evening of day D" (the demo narrative), only use:

| Source | Available at evening D if… |
|---|---|
| `erp/sales`, `pos_lines`, `kpi`, `traffic` | `business_date ≤ D − 1` (certified the next day; same-day sales are what the notes front-run) |
| `erp/inventory` | `snapshot_date ≤ D − 1` |
| `erp/forecast/sku_store_weekly` | `run_date ≤ D` (Mondays) |
| `store_emails` | `Date:` header ≤ evening D in the store's time zone |
| `internal_comms`, `systems/*` logs and tickets | own timestamp ≤ D |
| `external/weather` observations | date ≤ D; forecast file only if issued ≤ D (the only one is issued Oct 22) |
| `external/tourism` | publication date ≤ D (most monthly series lag 1–3 months) |
| `external/social`, `news` | published/collected ≤ D |
| `reports/` | the report's period end + issue date ≤ D (e.g. the Sep MBRs are issued in early Oct) |

---

## 5. Dev / hold-out split (recommended, agree as a team)

- **Dev (tune here):** MIL01, MIL02, PAR01, LON01, MUN01, MAD01, NYC01, TYO01, SEL01, SHA01, HKG01, SYD01, plus whatever else is not in hold-out.
- **Hold-out (only for the final metrics table):** ROM01, PAR02, LON02, ZRH01, NYC02, TYO02, SEL02, BJS01, TPE01, DXB01.

The hold-out still covers every storyline: construction (ROM01), black Maire (PAR02, LON02), cold (ZRH01), POS outage (NYC02), pink ILVARO (TYO02, SEL02, TPE01), POLARIS (BJS01), Gulf tourists (DXB01).
Also keep the team's hand-written hold-out notes (design doc §7.2) separate from all of this.

---

## 6. Where our design scenarios live in this data

| Design scenario | Concrete case(s) to use |
|---|---|
| S1 size stock-out with unmet demand | MIL01 LOGO CARDIGAN **size M**, sold out Thu 2026-10-08; DC has none until end of Oct |
| S2 tourist-driven colour demand | **black MAIRE** at PAR01, PAR02, MIL01, LON02 from ~Sep 19 (Korean tourists, Chuseok); DC empty until Oct 16 |
| S3 construction, traffic halved | **ROM01** Via Condotti scaffolding Sep 14 → Nov 6 (−50% footfall). It must NOT become "demand down" |
| S4 cold snap (A with notes / B context only) | A: MUN01, ZRH01, BER01, CPH01, AMS01 Oct 12–19. B: Paris, London and Milan get milder cold with fewer notes |
| S5 new product, no history | **ILVARO powder pink (510)** in Asia after the idol photo on Oct 1; also AMBRINE brown, ARNEB, POLARIS |
| S6 decoys | many: wrong colour/model names, corrected figures, gross-vs-net, staff exaggerations (see the answer keys) |
| S7 phantom inventory / data discrepancy | MIL02 says "only one cardigan M" while stock shows 3; COU01 stock after seasonal return; MAD01 received navy MAYA instead of black |
| S8 ambiguous product | "粉紅 Bady" (HKG01 meaning ILVARO), "Maire pink", MIL01 writing "Maya" for Maire |
| Forecast-bias case | **SYD01**: event-blind forecast ~2.5× too high on down jackets (southern spring) |
| Agents / handoff | SEL01 customs hold (KC certificate), BER01→PAR01 transfer rejected after cut-off, lane matrix for transfers |

---

## 7. `ground_truth/` (eval only, see R2/R3)

| Path | Use in M14 |
|---|---|
| `scenario/events.json` | all planted events (stores, dates, SKUs, multipliers) + DC stock-outs, with demand/sales/lost units per event |
| `demand/true_demand_window.csv` | per day×store×SKU: realised demand, event-free expectation, true expectation → **WAPE baseline vs corrected** |
| `demand/lost_sales_daily.csv` | unmet demand per day×store×SKU×size → **unmet-demand recall**, "never visible in sales" |
| `answer_keys/emails/emails_<lang>_notes.md` and `*_index.csv` | which email carries which signal, wrong/misleading emails, missing days → **extraction precision/recall labels** |
| `answer_keys/{reports,external,systems,internal_comms}_notes.md` | every metric definition, contradiction and data-quality trap, with the correct reading |
| `canonical/` | clean weather and FX behind the messy provider files |
| `writer_inputs/email_context/` | the per-day facts the email writers were given (debug only) |

Known cross-source discrepancies (they are in the data on purpose or accepted):
- SEL01 customs: `erp` shipments say planned Oct 12 / actual Oct 13, while the carrier and emails say promised Oct 8.
- COU01 stock still shows ~216 units after the seasonal return to the DC.
- ~130 completed inter-store transfers in `systems/logistics` are missing from `erp/inventory`.
- MIL02 and LON01 receive AMBRINE-brown requests but don't carry it, so those lost sales exist only in the emails.

---

## 8. Regeneration (dataset owner only)

- Core: `.venv/bin/python generator/world.py` (seeded; rewrites `sources/erp/` and `ground_truth/{scenario,demand,writer_inputs}`).
- Areas: `generator/<area>/` → `run_all.py` / `run_all.sh` / `build.py`.
- Scenario: `generator/events.py`. Briefs: `generator/WORLD_BRIEF.md` and `generator/EMAIL_SPEC.md`.
- Python env: `uv venv .venv && uv pip install --python .venv numpy pandas openpyxl xlsxwriter reportlab python-pptx python-docx pyarrow matplotlib pyyaml`.
