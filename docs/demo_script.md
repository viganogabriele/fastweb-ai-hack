# Demo script — 4 minutes (dev stores only)

**Track:** Moncler (FastwebAI Hackathon 2026). **Status:** draft, dev only.  
**Rule of the demo:** every number shown is rendered from a structured ref by a template;
the LLM cites artifact ids it can see and cannot approve, book or override a check.
**Offline:** all LLM and external calls are replayed from the cache; the demo runs with the
network off. **No transfer is required to succeed and no uplift is claimed** — the cardigan
case is allowed to end in `verify`, and the what-if branch is illustrative.

Owner: lane D. Source narrative: `docs/project-design.md` §9; cases: `generated/README.md` §6.

---

## 0:00–0:30 · The world tonight

**Screen:** case queue, sorted by priority and deadline. Clock shows Thu 2026-10-22 evening.

**Speaker:**
> "Tonight is Thursday. Sales for today do not exist yet — certified data arrives tomorrow
> morning. Unmet demand never arrives at all: if a size is sold out, the sale simply does not
> happen and nobody writes it down. Our pipeline reads what people write instead."

**Action:** open the Sources view, show a closing email in Italian with a highlighted span.

**Point:** the evidence is the quote, with code-point offsets into the canonical document.

---

## 0:30–1:15 · From a note to a linked observation (S1, MIL01)

**Screen:** MIL01 closing email, 2026-10-08, Italian. Span highlighted: "il cardigan logo M è finito, ce lo chiedono in continuazione".

**Speaker:**
> "A store manager writes this at closing time. The LLM extracts two things: a stockout with
> an exact zero, and an unmet-demand signal with no invented number — 'in continuazione' is
> vague, so it stays vague. No uplift is imputed."

**Action:** show the `Observation` with its `Evidence` (document, segment, quote, offsets);
show the `EntityLink` to SKU `LOGO CARDIGAN` size M at MIL01, with confidence and the
ambiguous alternative left visible.

**Point:** linking is a constrained choice over candidates, not a guess; an ambiguous mention
stays `verify` instead of being forced.

---

## 1:15–2:15 · The investigator runs (D1, MIL01)

**Screen:** case detail for the cardigan case. Baseline panel, scenarios/abstention reason,
tool trace, options with checks.

**Speaker:**
> "The agent cannot approve anything. It can only read: evidence, stock, lanes, options. Watch
> the trace."

**Trace shown (live):**
1. `get_case_evidence(case-D1)` → observations, candidates, periods, origins, uncertainties.
2. `get_available_stock(LOGO CARDIGAN, M, [MIL01, MIL02])` → MIL01 zero, MIL02 three on hand,
   snapshot date, quality holds.
3. `evaluate_options(case-D1)` → hold/verify/ask/notify, plus one domestic transfer with every
   check from RFC §4.10.

**Speaker:**
> "MIL02 says 'only one cardigan M' while stock shows three. The agent does not reconcile
> that silently — it surfaces the discrepancy as its own card. If the donor prerequisite fails,
> the case ends in `verify`, which is a valid result, not a failure."

**Action:** open the what-if panel.

---

## 2:15–3:00 · What-if and a second case in 20 seconds (S3, ROM01)

**Screen:** what-if: raise MIL01's forecast; the transferable quantity falls and the
recommendation changes. Then switch to the ROM01 case.

**Speaker (what-if):**
> "Raise the forecast and the same option shrinks. Numbers come from structured refs and
> templates, never from prose the model wrote."

**Speaker (ROM01, 20 s):**
> "Low sales in Rome. But the store note says Via Condotti is scaffolded until 6 November.
> The pipeline evaluates the case and freezes the forecast: no stock is pulled, and retail ops
> gets a construction card instead of a demand-down signal."

**Point:** silence and old stock do not close a case; `decision_due_at` is set when estimable.

---

## 3:00–3:40 · Ambiguity handled, not hidden (D5, dev store)

**Screen:** an ambiguous note ("a sweatshirt", colour unknown). Case status `verify` with two
candidates (hoodie vs crewneck). Simulated clarification reply in the store's language.

**Speaker:**
> "When the product is ambiguous the agent stops and asks the store in its own language. A
> teammate types the reply live; the case links afterwards. No match is imposed by an example."

**Action:** type the reply; show the case moving from `verify` to linked, with the new
observation and the updated trace.

---

## 3:40–4:00 · Metrics and market need

**Screen:** metrics slide (from the eval harness, M14): observation precision/recall on labelled
dev files, link errors among accepted links plus abstention rate, lead time vs sales and stock
baselines, false alerts, "not detected by T_end".

**Speaker:**
> "Everything is measured on dev stores only; hold-out stores are reported separately. All
> data is synthetic and declared as such."

**Market need (last 10 s):**
> "The buyer is HQ allocation and planning. Stores change nothing in their routine. Integration
> goes through the MCP layer vendors are already adding — no new system for the store."

---

## Dev-only notes

- Cases used: D1 (MIL01 cardigan M), D2 (Maire black, PAR01/MIL01), D3 (MUN01 cold, as context
  only), D4 (TIB zip, ARNEB fit), D5 (ambiguous mention), S3 (ROM01 construction). All dev
  stores per `generated/README.md` §5; hold-out stores are never shown.
- The script assumes the W42 retail flash and the MIL01 mailbox are available at as_of
  2026-10-22 evening. It does not require a feasible transfer or an uplift to land.
- Backup: a recorded run replay (cache on disk) reproduces the same trace with the network off;
  a second recording exists for the ambiguous case.
- S6 (wrong colour/model, corrected figures, gross vs net, exaggerations) and the decoy emails
  are kept out of the live path; they are in the eval set.

## Open items for the next draft

- Confirm timings with a stopwatch; trim the what-if to 30 s if needed.
- Add the exact screen captures once PLT-06 routes are frozen.
- Decide whether to show the cold-snap case (D3) or replace it with the TIB quality case (D4)
  depending on what is most stable on dev.
