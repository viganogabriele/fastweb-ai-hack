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

Validation: `make check`, `npm run build` in `web/`, and browser verification of
product grouping, filters, case navigation and run changes. Regression tests cover
run isolation, corrections/latest versions, unresolved scopes, overlapping
evidence and combined filters.
