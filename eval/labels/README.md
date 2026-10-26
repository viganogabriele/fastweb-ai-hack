# Reading labels (eval only)

Files in this directory are answer material. Only `eval/` code reads them (RFC §7.1). Product
code, prompts, fixtures, caches and the product `data/` namespace never do.

| File | Split | Written | Use |
|---|---|---|---|
| `reading_dev_v1.yaml` | dev | 2026-10-23, from the email text and the answer keys | EVL-02 (#124), tuning allowed |
| `reading_holdout_v1.files.txt` | hold-out | 2026-10-23, before `freeze-g3`, file names only | pre-registered EVL-02H sample (#126) |
| `reading_holdout_v1.yaml` | hold-out | after `freeze-g3`, from the email text only | EVL-02H, scored once, never tuned on |

## EVL-02H hold-out sample (pre-registered before `freeze-g3`)

The protocol (`docs/holdout-evaluation-protocol.md` §2) asks for hold-out labels on every
email in the approved store/day windows. The full window has 533 files. Nobody can hand-label
that many in the time left, so #126 scores a **deterministic stratified sample**. It is fixed
here, before the tag and before any hold-out email body was read:

- **Eligible files**: every `generated/sources/store_emails/<STORE>/*.eml` of the 10 hold-out
  stores (`config/eval_split.yaml`) whose `Date:` header falls on a store-local calendar day in
  2026-08-31..2026-10-21, inclusive. This is the same rule as the rolling runner's reading pass
  (`protocol.json` `reading_files`). Eligible: 533 files (BJS01 54, DXB01 53, LON02 54, NYC02 55,
  PAR02 52, ROM01 57, SEL02 52, TPE01 53, TYO02 54, ZRH01 49). The SHA-256 of the newline-terminated
  eligible list is `b6e1499157da18c9d1250882d128d17b2dc1ed9d331401c2e90d165e6452547d`.
- **Selection**: per store, order eligible files by
  `sha256("EVL-02H/reading-holdout/v1|<STORE>/<file>")` and take the first **11**. The result
  is 110 files, 11 per store. By store language: it 11, fr 11, de 11, ja 11, ko 11,
  zh-CN 11, zh-TW 11, en 33 (LON02, NYC02, DXB01).
- **Stratification** is by store, so each hold-out language is represented. Within a store the
  hash decides. Duplicates (`_dup`), replies (`_re1`), forwards (`_fwd`), wrong-list mails
  (`_wrong`) and no-signal mails enter in their natural proportion. None of them are
  oversampled or dropped.
- **List**: `reading_holdout_v1.files.txt`, SHA-256
  `b70f634bcd40800ac698d7a794c57dca5ce2b9e4254c77abe114016eaa7939b0`. To recompute it, run
  `backend/.venv/bin/python -m eval.holdout sample`. The code is in `eval/holdout.py`.
- **Scoring check**: `eval.holdout reading` asserts that the labelled files are a subset of the
  frozen protocol's `reading_files` and equal this selection recomputed over that list. Any
  other document in the export is outside the labels and is not scored. Precision therefore
  counts only observations on the 110 sampled documents.

The selection uses file names and Date headers only. No subject, claim, answer key or product
output took part in it.

## Hold-out annotation guideline (`reading_holdout_v1.yaml`)

Labels are written **once, after `freeze-g3`**, from the canonical email text only. The text
comes from `eval.holdout annotation-pack`, which uses the product's ING-02 parser and hands out
nothing but text, subject, reply/forward flags and attachment names. Annotators may consult the
source catalog `generated/sources/erp/master_data/` (`styles.csv`, `sku_colour.csv`,
`sku_size_ean.csv`) to resolve product codes. They never see answer keys, ground truth,
`generator/`, `*_notes.md`, the dev labels as answers, or any product output (exports, caches,
predictions). There is no adjudication against the product.

**Disclosure**: the hold-out labels are **AI-drafted**. Two independent annotator agents label
each file from the text alone, and a third agent reconciles them. Unless a maintainer reviews
them, they are not human-reviewed, and every report must say so.

### Schema (same as `reading_dev_v1.yaml`, scored by `eval/reading.py`)

```yaml
version: 1
sample: {split: holdout, criterion: "...", seed: "EVL-02H/reading-holdout/v1", per_store: 11}
files:
  ROM01/20260903_2031_ROM01.eml:
    language: it            # the store language from stores.csv, set mechanically
    note: optional free text (no-signal mail, ambiguity, attachment-only)
    labels:
      - {id: rom01-0903-sales, anchor: "...", kinds: [sales_figure], required: true}
```

- **One label = one business fact** that the mail states. Label facts in the sender's own text.
  In quoted parts (see `quoted_spans`), label only new information carried by a forward, for
  example a customer complaint forwarded to HQ. Never label a quoted repeat of the store's
  earlier mail.
- `anchor`: the shortest exact substring of the canonical `text` that states the fact, copied
  character by character, including whitespace such as tabs. It must occur **exactly once**;
  if it does not, extend it. Never use the subject: it is not part of the text.
- `kinds`: every observation kind a careful reader could accept for that fact, from the
  extraction taxonomy: `unmet_demand`, `demand_up`, `demand_down`, `stockout`, `low_stock`,
  `stock_discrepancy`, `product_feedback`, `traffic_change`, `customer_profile`,
  `operational_issue`, `sales_figure`, `local_event`, `other`. Put the most natural kind first.
  Add acceptable alternates (for example a traffic count: `[traffic_change, sales_figure, other]`),
  but no kinds that misread the fact.
- `required: true` for core signals: the day's sales against budget, stock-outs and low stock,
  unmet demand (customers asking for what the store could not sell), clear demand up/down for a
  product, returns, defects, fit or quality feedback, a customer profile that explains demand, a
  local event, weather or holiday the store ties to business, and stock discrepancies or
  operational problems that affect selling. `required: false` for valid but minor facts:
  traffic or conversion counts without comment, lists of items sold, a delivery received on
  time, greetings-level remarks.
- `product`: the catalog id the store means, at the finest level the text fixes. Use a
  style code (`J20931A00012`) when no colour is given or the colour names several SKUs, a SKU
  (`<style>-<colour>`) when one colour is named, and a SKU-size (`<sku>-<size>`) when exactly
  one size is named and it exists in `sku_size_ean.csv`. Resolve product words through the
  catalog names, codes and colours. **When the text plus the catalog do not identify a single
  style, leave `product` out and explain in the file `note`. Never guess.** Facts about no
  product (sales, traffic, events) have no `product`.
- `level: style` only when the product is a style and a SKU-level link would be wrong: the mail
  gives no colour at all, or the colour it names does not exist for that style in the catalog.
- `negated: true` when the correct reading is that the fact did not happen ("no requests
  today", "nessuna richiesta"). Omit it otherwise.
- `id`: `<store lowercase>-<MMDD of the file name>-<short slug>`, unique in the file. Add the
  suffix for `_dup`, `_re1` and similar files (for example `dxb01-1018dup-sales`).
- Files with no business facts (out-of-office, wrong list, retraction, attachment-only,
  courtesy reply) get `labels: []` and a `note`. Any observation the product extracts there
  is then a false positive.

Quantities and periods are not scored (`eval/reading.py`). Annotators still anchor the words
that carry them, so the evidence span covers the fact.

### Workflow after the tag

```sh
P=backend/.venv/bin/python
$P -m eval.holdout annotation-pack --output-dir data/eval/evl02h/pack   # text only
# annotate (two independent passes) and reconcile into eval/labels/reading_holdout_v1.yaml
$P -m eval.holdout check-labels --labels eval/labels/reading_holdout_v1.yaml  # prints SHA-256
```

After `check-labels` passes, the file is committed once with its SHA-256 and never edited
again after scoring. A defect found later follows protocol §8: the old file and its results
are preserved, and the re-scoring is disclosed.
