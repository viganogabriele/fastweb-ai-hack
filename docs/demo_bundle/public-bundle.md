# Public demo bundle (DEMO-03)

Esempio sintetico, nomi sostituiti. Synthetic example, names substituted.

This is the sanitized public projection of the recorded dev run, built with the existing
DEMO-03a builder ([README.md](README.md)). It is a **release candidate kept local**: the bundle
lives in ignored `data/public-demo/`, as the builder requires, and is **not uploaded or
published**. Public release is a separate, explicit action for the maintainer.

## Disclosure (ship this text with the bundle)

- **Synthetic data.** Every email, store, product, sale and stock figure was generated for the
  hackathon challenge, with decoys and noise. Names of people, the brand, a department store, a
  street, a logistics site, a phone number and the original product family code were replaced
  with fictional ones before export (`replacements.json`).
- **Recorded, simulated execution.** The source run is `core-dev-candidate`, `mode: recorded`,
  status `degraded`, namespace `product`, as of 2026-10-22 20:00 UTC, dev stores MIL01, MIL02,
  MUN01, NYC01. Model and warehouse/logistics responses were recorded once and replayed offline.
  Warehouse and logistics systems are simulated; every decision is a local draft and nothing is
  sent or moved.
- **No performance claim.** The bundle holds evidence, facts and cases only. It certifies no
  replay, accuracy, uplift, ROI or causal result. Measured results are in
  `docs/holdout-results.md` `[PENDING #128]`.

## Build

From the repository root, on the recorded run rebuilt by `make demo-data`:

```sh
mkdir -p data/private-demo && chmod 700 data/private-demo
# once: a private HMAC key (never commit or share it; ids depend on it)
(umask 077; backend/.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))' \
  > data/private-demo/reference_key)
backend/.venv/bin/python scripts/export_public_demo_manifest.py \
  --db data/demo/current/data/tesseract.db --run-id core-dev-candidate \
  --key-file data/private-demo/reference_key --output data/private-demo/approved-demo.json --approved
backend/.venv/bin/python web/scripts/build_public_demo.py data/private-demo/approved-demo.json \
  --output data/public-demo --private-map data/private-demo/mapping.json
```

`export_public_demo_manifest.py` only selects artifacts; it changes no text. It exports the
current version of every `SourceDocument`, `Segment`, `Observation`, `Case` and `Report` of the
run. Case `context_refs` to kinds the builder does not project (`EntityLink`,
`EvidenceRelation`, `ContextEvent`) are dropped, since they would exclude every case as a
dangling reference. All sanitizing, offset rebuilding and exclusion is done by the builder.
`data/private-demo/` (input manifest with original text, key, private map) never leaves the
machine.

## Candidate built on 2026-10-23

| File | sha256 |
|---|---|
| `artifacts.json` | `085fab2eeaa036668dd7675238e946f168d20fc5f8f28ea0dfa4c8a9a4cd8ec5` |
| `manifest.json` | `5b950bf43d1a6979a8f0da2396ef0943fac837a27adf3216e14e0288209ee5b0` |

Built from code `1f7f355` (frozen candidate) plus this exporter, on a fresh replay attempt of
`core-dev-20261023` (output `9346b85e…a56f`). A second build from the same manifest and key, and a
re-export from another fresh replay attempt, gave byte-identical manifests and files. The ids are HMACs of the private key, so another key gives other ids and
hashes with the same content.

`manifest.json` carries `"synthetic": true`, the builder notice, the file hash, one hash per
included artifact and every excluded artifact with an opaque id and a reason code.

| Kind | Included | Excluded (reason) |
|---|---:|---|
| SourceDocument | 11 | 1 `unresolved_sensitive_text` (an out-of-office email with an address), 1 `missing_dev_store` (the W42 controlling workbook) |
| Segment | 32 | 174 `ambiguous_or_excluded_document` (segments of the workbook) |
| Observation | 82 | 0 |
| Case | 38 | 0 |
| Report | 0 | 2 `dangling_or_excluded_reference` (they cite forecasts and options, which are not projected) |

Not exported by design: original URIs, headers, senders, threads, attachments, locators, entity
links, evidence relations, forecasts, options, traces, clarifications, decisions, raw model
responses and execution metadata (builder projection policy).

## Review (2026-10-23)

- **Text.** All 11 public documents were read in full. No email address, URL, path, filename,
  header, phone number, brand or real department-store name remains. Remaining place names are
  cities (Milano, München, Roma, Monterrey) and the nickname "Monte". First names are fictional
  replacements; signatures like "G." and "R." are initials only.
- **Offsets.** For every segment and every evidence quote, the quote equals the code-point slice
  of the sanitized document and lies inside its segment: 0 mismatches over 32 segments and 82
  quotes, including `ß`, `ü` and text shortened or lengthened by replacements.
- **Store scope.** Only the four dev stores appear; the builder excludes any other store id.
- **Metadata.** Public fields per kind are those of the builder README; opaque store and owner
  references replace ids. No timestamps or local paths.

## Release

Before any public use (separate decision, not implied by this build):

1. Re-read `data/public-demo/artifacts.json` against this page; confirm the replacements are still
   complete for the final run.
2. Publish only `data/public-demo/` together with the disclosure above. Never publish
   `data/private-demo/`, the replay database, `data/fixtures/runs/`, screenshots or videos of
   the real UI: those show original synthetic names and source URIs.
