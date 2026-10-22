# Findings — Moncler track (FastwebAI Hackathon 2026)

_Last updated: 2026-10-22._
_A synthesis of everything in `sources/`, plus what the organizers told the team in person. Facts are kept apart from our interpretation, and passages where the transcript is garbled are marked._

> Confidentiality: the Moncler rep asked us **not to cite them** ("non citateci", `sources/transcripts/Poke House.md:49`). In anything public — project name, slides, repo, demo data — use a neutral name and a fictional luxury brand unless the organizers say otherwise.

---

## 1. Source map

| File | What it actually is | Reliability |
|---|---|---|
| `sources/track/track.html` | Official track text ("Forecast che ascolta i negozi"), complete | High (transcribed from the printed card) |
| `sources/track/eval.html` | Jury voting method | High; category names were partly cut off in the photos |
| `sources/transcripts/Poke House.md` | ASR (automatic transcript) of the opening pitches: Alpitour 00:00–05:23, **Moncler 05:23–10:45**, then the moderator. The filename is misleading. | Medium-low |
| `sources/transcripts/Poke House 2.md` | ASR (Whisper `small`, uncorrected) of **our Q&A with the Moncler rep**. Its header says "Poke House 3". | Low: the gist is reliable, the exact wording is not |
| `drafts/fastweb.md` | The team's v0 proposal ("MONCLER PULSE"), written before we had the full track text, the Q&A or the scoring. Partly superseded; see §7. | — |

---

## 2. The problem, as officially stated (`track.html`)

- A brand with stores in many countries sells thousands of products a day. Someone has to decide **what to replenish, where to move stock, and what to tell customers**.
- A sales forecast exists at several levels (product, store, region), but it "looks only at the numbers, and the numbers arrive after the facts. The stores see the facts first."
- Every evening each store sends a **closing email with free-text comments in its own language**. Official examples:
  - *"tanti turisti coreani, chiedevano la versione nera"* (lots of Korean tourists, they were asking for the black version)
  - *"taglia M finita da giovedì"* (size M sold out since Thursday)
  - *"cantiere davanti all'ingresso, passaggio dimezzato"* (construction site in front of the entrance, foot traffic halved)

  There are hundreds a day, written in a hurry, and almost nobody cross-checks them against sales.
- There are also market, campaign, channel and country **reports in PDF, Excel and slides**, with metrics defined differently and sometimes contradicting each other.
- Then there's **external data**: events, weather, tourist flows, calendars, trends.
- The challenge: build a system that combines forecast, store signals, reports and external data, and turns them into **useful guidance for decision makers**. Warehouse, logistics, marketing and planning each have their own tools and, more and more, their own agents.
- Expected deliverable: a **concept plus a working prototype** in which numbers, comments, reports and external data together produce **one concrete recommendation**. Nice to have: **new products with no history**, and **integration with other agents**.
- The organizers **shared the problem, not a priority**. Going deep on forecast correction, on store-data ingestion, or on a mocked full pipeline are all legitimate interpretations.

---

## 3. What the Moncler rep added

Line references point to `sources/transcripts/Poke House 2.md` unless stated otherwise. This is our reading of a garbled transcript; ⚠ marks the passages that are hardest to read.

1. **Deliberately open.** He wants to see how we put a complex system together and which blocks we choose to focus on. A full agentic system that talks to the other systems is fine; focusing on a single block is "absolutely fine". "Focus on what interests you most… it's an exercise, not an exam." (7–38, 121–124)
2. **His mental model.** Data sources (more or less structured) feed systems that use them, end to end: product creation (descriptions, prototypes) → transactional and management systems (what you sell) → marketing and communication. (8–15)
3. **Some pieces can't be moved:** the forecast models and the data/transaction management systems. They are **slow by design**: forecasts learn from history, which at best means last season, a year ago. (15–23)
4. **Stores have the real-time grip.** A failed campaign, a geopolitical shock or a product going viral shows up in the numbers only slowly. (24–30, 86–89)
5. **Store reports** differ by country and by store. They are written by hand and arrive as email, PDF or Excel. A free-text comment from the store manager is almost always there. (38–42)
6. **AI today.** AI isn't really used on this process. Adoption is happening through **vendor systems: management systems/ERP exposed via MCP, with agents you can talk to**. Classic ML models also exist. ⚠ (42–46)
7. **"So we correct the forecast?" — "Yes."** The underlying question is where in this long chain AI helps anticipate the market. It should tell you, **weeks before the actuals**, that you need to act. (48–53)
8. **Actuals** (receipts, sell-out) are **certified and arrive about 24h later**. "We don't need to dismantle that." A stockout in another time zone is known at HQ the next day. Stores give you information, not certified data. (54–64)
9. There are **two ways to "change the forecast"**: retrain the model with the new data, or **support decisions by explaining what's happening** (example: the shop window was smashed the day before). (65–68)
10. **Report format.** We floated a dashboard where stores upload their files. ⚠ It's unclear whether he said the store's own reporting must stay as it is. He then invited us to **generate example reports, and he'll tell us whether they make sense** ("potere alla fantasia", let imagination rule). (69–74)
11. **The cost of a stockout** is not only the lost sale but **damage to the brand image**. The real problem is "making decisions as early as possible". (79–85)
12. **Scarcity.** On our example of a brand that deliberately caps an evergreen product: insights such as "we should change the planned scarcity" are welcome, but **humans decide**. **Short term** means moving stock between regions or stores. **Long term** means changing production, which is very high-stakes. Not every decision is 100% AI. (91–111)
13. **Real constraints exist** (forecast cadence, timings, …). ⚠ (127–130)
14. From the pitch (`Poke House.md`):
    - the Data & AI team is a few months old and is centralizing scattered AI initiatives alongside classic ML and forecasting (53);
    - hundreds of stores across regions, time zones and languages (57–61);
    - evergreen vs seasonal/new products, with seasonal ones harder (65);
    - stock is reallocated between regions and warehouses (69);
    - store reports are "un casino" (a mess) (73);
    - the same information also feeds marketing: which product is doing well, what will work next year, social, age groups (77).

---

## 4. How we're scored (`eval.html`)

| Category | Weight | What it really asks |
|---|---:|---|
| Aderenza alla challenge (fit with the challenge) | 10 | Did we address the Moncler problem? |
| **Completezza e realizzabilità** (completeness and feasibility) | **40** | Does it work end to end, and is it believable? **Also the first tie-breaker.** |
| Innovazione agenti AI (AI-agent innovation) | 20 | Is there a genuinely agentic part (tools, choosing the next step, talking to other agents)? |
| Potenziale applicativo (application potential) | 10 | Could it be used for real? |
| Allineamento tecnologico (technology alignment) | 10 | **Per the organizers: how well it fills a real market need.** |
| Qualità dell'esposizione (presentation quality) | 10 | The pitch |

- Each juror gives one integer vote from 1 to 5 per category. The sub-criteria are guidance only. Missing votes don't count as zero.
- These are the weights from the rules. The ones actually in force appear in the organizers' leaderboard, so check them on the day.
- **Implications:**
  - 40% rewards a narrow path that demonstrably works over a broad one that's half mocked.
  - 20% means at least one LLM component must *act* (call tools, decide, ask), not only extract.
  - The market-need 10% means we must name the buyer, the pain, and why existing tools don't cover it.

---

## 5. Domain knowledge we lean on (general retail practice, not from the rep — confirm if it becomes central)

- **Censored demand.** Sales ≠ demand. When an item is out of stock, POS sales record zero and the forecast learns the lower number. A customer asking for size M when there's none is **invisible** in sales data; a store note is often the only trace.
- **Phantom inventory.** System stock and shelf stock disagree. A note saying "M finita" while the system shows 3 on hand is a data-quality signal.
- **Sizes.** Stockouts happen per size, and a model can be fine overall while its core size is gone.
- **Luxury specifics:**
  - replenishing from a regional warehouse (DC) usually comes before a store-to-store transfer;
  - transfers across customs borders (EU↔UK, EU↔CN) are expensive or impossible;
  - markdowns are rare, so excess stock is costly too;
  - scarcity is sometimes **intentional**, so a stockout is not always a failure.
- **Report heterogeneity** typically comes from:
  - several definitions of sell-through;
  - retail (4-5-4) vs calendar weeks;
  - VAT-inclusive vs VAT-exclusive figures;
  - gross vs net of returns;
  - local currency vs EUR, and at which exchange rate;
  - like-for-like vs total.
- **Tourism drives European luxury demand.** Nationality-specific holidays and tax-free shopping flows matter. The official Korean-tourists example points here.

---

## 6. Things to look out for

### Framing
- **Don't build a better forecast model.** Their models are fixed and slow by design. We add a layer that **corrects or annotates** the forecast with same-day store evidence. Treat the baseline forecast as a given input.
- **Don't replace certified reporting.** Store signals are *uncertified*. Show them visibly apart from actuals and never blend the two silently.
- **"Earlier" is the whole value proposition.** Every claim should be stated as "the system knew on day D; sales data would have shown it on day D+k, or never".
- **Humans decide.** The output is options with evidence, never executed actions. That matters most for the long-term ones (production, scarcity).

### Ingestion
- **Real notes contain no SKU codes.** They say "la versione nera", "the Aurore in M", "the long one". Linking text to products is the hardest and most valuable step. Narrow the candidates using what the store actually stocks and recently sold. **When the text is ambiguous, ask; don't guess.** A wrong confident link is worse than no link.
- **One note holds several claims of different types** (demand, operations, customer profile). Split them before classifying.
- **Time:** resolve relative expressions ("da giovedì", "depuis hier" = since yesterday) against the note's business date, in the store's time zone.
- **Negation and state:** "ancora disponibile" (still available) is not a stockout, and "non più" (no longer) is.
- **Dedup and state:** the same issue repeated on three evenings is one ongoing signal, not three new ones. Also track when a signal is resolved.
- **Vague quantifiers** ("plusieurs", "tanti", "a few") should become **ranges**, never a single number.
- Keep the **verbatim original span** as evidence and use translation only for display. Check that the evidence span really occurs in the source.
- **Personal data:** notes can name VIP clients or staff. Redact them before anything is stored or sent to an LLM.
- For structured reports, let the LLM **propose a column/metric mapping once**, have a person confirm it, and save it as a template that later runs without the LLM. If a metric definition is missing or conflicting, show the conflict rather than picking a number.

### Forecast and decisions
- The **numbers come from code**, never from the LLM. The LLM reads text; deterministic functions compute the adjustments and quantities.
- **Use ranges.** Turn a range into a quantity with an explicit service-level policy. Stockouts cost more than excess in luxury (brand damage), but excess isn't free either.
- **Operational disruptions run the other way.** Construction or a broken window means low sales ≠ low demand. Those days must be **excluded** from "demand is down" conclusions and flagged for retraining.
- **Use external data as context, not as a trigger.** A cold day alone doesn't prove sales will rise. It raises confidence when store notes agree, and shows up as context otherwise.
- **Options must be feasible:** respect the donor store's own needs and safety stock, reserved units, lead time vs the date stock runs out, cross-border rules, and size.
- **Respect scarcity-managed products:** produce an insight, not a "make more" recommendation.

### Trust, evaluation, honesty
- All demo data is **synthetic**; say so. Never present it as Moncler data or as a trained model's results.
- **Circularity risk:** if we generate notes from planted events, then detect them, it proves little unless the test set also contains noise, omissions and decoys. The extraction prompts must not be tuned on the hold-out set. Ideally the rep reviews sample notes.
- **Show "does no harm" too:** on decoy and noise scenarios the adjusted forecast must stay close to the baseline.
- **Offline replay:** cache every LLM and external call, so the live demo can't fail on the network.

### Pitch (market-need angle)
- **Buyer:** merchandise planning and allocation at HQ, with retail ops and marketing as secondary users.
- **Pain:** decisions lag reality by days or weeks, and unmet demand is invisible.
- **Why now:** LLMs make multilingual free text machine-readable, and vendors are exposing systems through MCP.
- **Adoption argument:** **stores change nothing**, because we read the emails they already write.
- To validate with the rep: our impression is that commercial demand-sensing tools work mostly on structured feeds (POS, weather, promotions) and leave qualitative store intelligence to humans.

---

## 7. What's superseded in `drafts/fastweb.md`

| Draft says | Now |
|---|---|
| Name "MONCLER PULSE", speaker named | Rename to something neutral; don't cite the company or the person |
| "We don't know the jury criteria" (§3) | Known; see §4 above |
| Demo note contains the SKU code "JKT-014" | Unrealistic: notes use names, colours and sizes. Product linking must be part of the demo |
| Only store→store transfers | Add DC replenishment, hold and no-action options; check cross-border feasibility |
| Questions for the rep (§10) | Partly answered (see §3); remaining ones are in §8 below |
| Still valid | LLM extracts while code computes; verifiable evidence; human approval; draft-only handoff; offline fallback; one end-to-end case before breadth |

---

## 8. Open questions (ask the rep, briefly)

1. Can we propose a light structure for store notes (optional fields, replies to clarification questions), or must we ingest them strictly as they are? He offered to review generated example notes, so **bring 5–10 synthetic notes and ask "realistic?"**
2. Which HQ role should the output target first: allocation/merchandising, retail ops, or marketing?
3. Is their forecast granular down to store × SKU × size? Over what horizons?
4. What lead times are typical for DC→store and store→store moves? Are cross-border store transfers ever done?
5. What is the most common pattern in store notes: product requests, stock issues, or operational problems?
6. Can the company name appear on the final slides, or should we use a fictional brand only?
