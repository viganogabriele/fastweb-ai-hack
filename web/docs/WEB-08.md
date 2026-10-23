# WEB-08: product view

`#/prodotti` groups the latest published cases in the selected run by their
explicit product identity. SKU, SKU-size and style are separate scopes; category,
store and unknown cases remain visible in a separate verification section.
Filters combine search, store, case status and signal type. Opening a case leads
to its versioned detail and source references in the same run; browser Back
returns to Products.

The view reads the existing `GET /api/runs/{run_id}/cases` contract. It does not
load the dataset, create a new API contract or use demo mocks. Loading, missing
runs, unpublished runs, errors with retry, empty results and filter reset are
handled explicitly. Run changes remount the data consumer and abort its request.

Counts describe cases, not units, customers, independent origins, returns or lost
sales. Source/document counts are not summed across cases. Motivations are labeled
as case motivations, not customer reasons or causal explanations. Quantitative
sales and returns are explicitly unavailable because the current API provides no
such series; no conversions or sales comparisons are inferred. A published run
without cases makes no claim about the absence of demand. Fixture runs retain a
visible demonstration label.

Scope exception: the requesting user explicitly authorized starting WEB-08 before
documented G2/reserve authorization and reassignment to `viganogabriele` in the
task conversation. This does not attest that G2 passed or authorize other reserve
tasks.

Validation:

- CI `check` passes. Locally, `PYTHONHASHSEED=0 make check` passes (1,368 backend
  and 16 frontend tests, lint, typecheck and generated API types). Plain
  `make check` encounters the existing isolation test's Python child startup error
  `_Py_HashRandomization_Init: failed to get random numbers to initialize Python`
  on this machine. No tests are skipped and isolation code is unchanged.
- `npm run build` in `web/` passes.
- Browser verification with isolated test API responses covers grouping, fixture
  labeling, search/reset, store filters, versioned case navigation and Back,
  390px mobile layout, empty/unpublished runs, error/retry and a delayed request
  returning after a run switch. No page errors or horizontal mobile overflow.
- Regression tests cover run isolation, corrections/latest versions, unresolved
  scopes, overlapping evidence and combined filters.
- `npx -y @memi-design/cli@2.7.9 diagnose web --json --no-write --fail-on none`:
  score 50 before and after, with no reported issues. Source review confirmed
  the existing `#/prodotti` placeholder, shared token-based cards and labeled
  field primitives; the change reuses these tokens and primitives and adds a
  single-column layout below 560px. The automated score is a broad heuristic,
  not an accessibility certification. No unrelated design changes were made.
