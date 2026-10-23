# Hold-out results display (#128), Could

Goal: if time allows, show the frozen evaluation results so a judge can read them next to the
product. The results must carry their denominators and limits, and must never be overclaimed.
Priority: **Could**. The default and recommended channel is the metrics slide of the pitch
(#129), not the product app. Do nothing here until #128 publishes reviewed outputs: today no
hold-out result exists (#128 is blocked by #211, #126, #127).

## 1. Constraints

- Product code never imports `eval/` or reads labels (`AGENTS.md`, "Hard rules"). A UI view may
  only display a **reviewed, exported** results file. It must not call the evaluator or
  compute metrics in the browser.
- The inputs are the outputs named in the protocol: `reading.json`, `lead-time.json`,
  optional `forecast-errors.json` (`docs/holdout-evaluation-protocol.md:223,251,265`). They are
  bound to the candidate SHA and artifact hashes recorded by #211/#128.
- Dev diagnostics and hold-out results are separate sections and never merged
  (`docs/holdout-evaluation-protocol.md:281-410`). Synthetic extensions are kept apart from
  forecast scoring (#128).
- Maximum claim wording: `docs/RFC-001-piattaforma.md:723`. No accuracy-as-business-value,
  uplift, ROI, "revenue recovered" (`docs/RFC-001-piattaforma.md:706`).

## 2. Acceptance criteria (if built)

- [ ] Static source: one approved JSON (copied from the #128 outputs, with its hash) served as a
      static asset or included in the public bundle. No API route, no live computation.
- [ ] Header: candidate SHA, evaluation date, protocol version, "dati sintetici", store
      universe (hold-out store list) and "nessun tuning dopo l'osservazione".
- [ ] **Reading/linking**: precision and recall with N and denominators, accepted-link errors,
      abstention share, per-language counts where annotated; otherwise "non disponibile".
- [ ] **Lead time**: distribution including zero and negative values, false alerts, missed
      events, "Non rilevato entro T_end" (`docs/RFC-001-piattaforma.md:699`), and the sales/stock
      baselines it was compared to.
- [ ] **Forecast WAPE/MAE** only when the fixed-universe export exists. Otherwise one line:
      "non disponibile: <reason from the output>".
- [ ] Every number has its denominator in the same visual unit. No rounding that hides small N.
- [ ] A "Limiti" box copied verbatim from the #128 report.
- [ ] Hold-out store cases never appear in the demo queue or screenshots
      (`docs/RFC-001-piattaforma.md:542`).

## 3. Manual test script

1. Load the page with the approved JSON. Check: SHA and hash match the #128 report.
2. Compare every displayed figure with the report table. Check: identical values, denominators present.
3. Remove `forecast-errors` from the JSON (local copy). Check: the page states it is unavailable
   and shows no placeholder number.
4. Search the page for "ROI", "uplift", "accuratezza del business". Check: absent.
