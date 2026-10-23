# Public demo bundle builder (DEMO-03a)

This CLI prepares a separate public **projection** of explicitly approved dev DTOs.
It does not modify sources, exports or caches, upload anything, certify replay,
calculate performance/ROI, or produce a pitch/video. Final review and release
remain in DEMO-03. It changes no application screens or mock middleware.

## Prepare and review the manifest

Run `make setup`. Copy `synthetic-manifest.json` from this directory to a new file
under `data/`. It contains only fictional, hand-written examples, including emoji,
CJK and a repeated quote. Its `approved` flag is deliberately false.

For real preparation, export only the explicitly approved dev artifacts into the
manifest's `artifacts` array as `{ "kind": "SourceDocument", "payload": { ... } }`.
No source filenames, globs, URLs, media or cache directories are accepted as inputs.
The tool reads the manifest and `config/eval_split.yaml`, never dataset files or an
answer key. All selected stores and any artifact store must be in the approved dev
set. Unknown/holdout stores fail before writing output.

Set `replacements` to an explicit dictionary of sensitive text → fictional text.
Matching is literal, longest-first and simultaneous, so replacements do not cascade.
Include every spelling/case needed in the approved text, including people, brands,
products, emails, filenames or locations. Targets must not contain sensitive source
tokens. Deletion via an empty target is allowed. Recognised residual emails, URLs, bare
domains, local/UNC/home paths, filenames, mail headers (in the dataset's languages), HTML,
Markdown links and credential patterns exclude the artifact. A configured sensitive token
that survives in any form also excludes it: the check runs on NFKC-normalised, case-folded
text without zero-width characters or soft hyphens, and again on letters and digits only
(so `Private-⏎House` or full-width variants are caught). Replacement itself stays literal:
add the variants you want substituted rather than excluded. Any store id outside the
approved `stores` in public text, or in a report citation scope, excludes the artifact.

Choose a fresh private `reference_key` of at least 32 characters for real inputs
(for example, locally generate one with `secrets.token_hex(32)`). Keep the key and
manifest private. The committed sample key is for synthetic examples only.
HMAC-derived IDs give stable references for the same manifest/key without exposing
the original IDs. Public artifact versions are `public-v1`; text versions hash only
sanitised text. The private map records original identities, source content hashes,
replacements and opaque store/owner identifiers. It is created with mode `0600`.

Review the exact input text and mapping, then set `approved: true`. The flag records
explicit input selection; it is not a general PII detector. Arbitrary names or facts
not covered by the reviewed mapping cannot be recognised automatically. Inspect the
derived output before any public use. Only the named public directory is a release
candidate; never distribute its input manifest or private map.

## Build

```sh
backend/.venv/bin/python web/scripts/build_public_demo.py data/approved-demo.json \
  --output data/public-demo \
  --private-map data/private-demo/mapping.json
```

All paths must resolve under `data/`, including through symlinks, and the output and
mapping must not be under a folder `.gitignore` versions (`!data/...`, e.g. `data/fixtures/`),
so a routine `git add` cannot commit them. The public
directory must be new; input and mapping must stay outside it. Existing outputs,
mapping files and originals are never overwritten. An unsuccessful build cleans
up only newly created output/map files. Identical inputs and key produce identical
public bytes and hashes; timestamps and local paths are not exported.

## Supported projection

This is a small public JSON format, not a round trip of private DTOs. Every field
not listed here is intentionally omitted, including original URI, headers, author,
thread, attachment, locator, raw model response and execution metadata.

| Kind | Public fields beyond opaque id/version |
|---|---|
| SourceDocument | Sanitised canonical text/text version, opaque store reference, source type. Voice/system API documents are excluded; no original media is copied. |
| Segment | Public document reference/text version, rebuilt canonical slice and code-point offsets. Original text version must identify exactly one included document. |
| Observation | Observation type, sanitised product/reason/time words, already structured quantity kind/unit/currency/raw/value/range, and rebuilt evidence. No counts, conversions or predictions are inferred. |
| Case | Sanitised case type/status/priority/reason, opaque owner and supporting/contradicting/context references. Every referenced artifact must already be included; private scope, product IDs, dates and aggregate counts are omitted. |
| Report | Sanitised Markdown and citations to included public fields. Original scope/period/unit metadata is omitted. Unknown citation fields or numbering exclude the report. |

Documents are processed before segments, observations, cases and reports. References
must resolve to an included exact original kind/id/version; unsupported dependencies
exclude the dependent artifact. Case→case and report→report references resolve
regardless of id order; cycles are not supported. A malformed artifact (missing or
mistyped field) is excluded as `malformed_artifact` instead of stopping the build. Other
artifact kinds, including agent traces and recordings, are explicitly excluded.

Evidence is checked against the original canonical slice **before** replacement.
Offsets are mapped from those original code-point boundaries, never by searching
for a possibly repeated quote. Every exported quote is the corresponding sanitised
document slice and lies in its exported segment. A boundary inside a replaced token,
a fully deleted quote, ambiguous versions or missing evidence cause exclusion.
No audio timestamps or replacement evidence are invented.

`artifacts.json` contains only the allowlisted public projection. `manifest.json`
marks the output synthetic, records public file/artifact hashes and lists opaque
excluded references/reason codes. Exclusion descriptors have their own hashes;
original excluded payload hashes remain in the private map. This avoids publishing
hashes of private originals. Omitted metadata is covered by the projection policy.

## Handoff and checks

DEMO-02 can feed this tool an explicit manifest exported from a reviewed dev run;
no dependency on its replay command or unmerged UI work is needed. The final frozen
demo, measured results, replay sign-off and reviewed release remain separate work.

```sh
backend/.venv/bin/python -m unittest discover -s web/scripts -p test_public_demo.py -v
backend/.venv/bin/ruff check --config backend/pyproject.toml web/scripts
backend/.venv/bin/ruff format --check --config backend/pyproject.toml web/scripts
make check
```

The web test runner invokes the same synthetic Python regressions during `make check`.
No real source, hidden answer, secret or holdout input is used by these tests.
