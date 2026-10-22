# MVP contracts v1.0 (PLT-02)

These Pydantic v2 DTOs implement RFC-001 §4.3–4.5 for the MVP handoffs in
`docs/PLAN.md` §3. Import public types from `tessera.core.contracts`.
The area files follow the producer ownership defined in the plan. `StockFact`
is in `common.py`; metrics and context are in `observations.py`; reservations
are in `options.py`; decisions and clarifications are in `agents.py`.
`RunContext` and executable module functions belong to PLT-04 and are not DTOs.

From the repository root, export all contracts to one JSON Schema 2020-12 bundle:

```sh
cd backend
uv run python -m tessera.core.contracts --output ../data/contracts/schema-1.0.json
```

Omit `--output` to write to stdout. Each public DTO is available under
`$defs/<ClassName>`. The same models can be used directly by FastAPI;
PLT-06 adds API routes and generates web types. Schema files are derived output.

## Validation boundaries

- Unknown fields are rejected. Optional source attributes default to `null`;
  required nullable measurements preserve missing values instead of making zero.
  `available_at=null` means availability is unknown and must be excluded by the
  strict replay repository. `availability_basis` records the source or convention.
- All instants require a timezone and normalize to UTC. Business days and forecast
  days are dates. All numbers are finite. Integer movement quantities reject booleans
  and fractional inputs. `computed_at` is processing time, not simulated availability.
- Counts, money and percentages have distinct units. Currency is required for numeric
  money. Count signs are nonnegative; signed money and percentage changes are allowed.
  Quantities never convert customers or requests to units. Parsing and checking a
  number against its source text belong to ING-09.
- Character offsets are half-open Python Unicode code point offsets into canonical
  document text. Before publishing a segment, call
  `segment.validate_against(document)`. Before publishing an observation, call
  `evidence.validate_against(document, segment)` for **each** evidence item. The latter
  verifies document version, segment membership, exact text, and any real audio
  interval. Structural Pydantic validation alone cannot resolve external records.
- Artifact references contain the exact `kind` (public DTO class name), `id` and
  `version`. Source references contain URI, content hash and an optional row/cell
  locator. Stable IDs/hashes, referential integrity, input availability maxima and
  run/scenario isolation are computed or checked by producers/repository, not invented
  by model defaults. Empty reference collections remain explicit rather than omitted.
- An unresolved link has no selected target or level; candidates retain their level
  and declared score scale. A score is not a probability. Fact corrections never
  target a whole `SourceDocument`.
- Missing forecast and scenario values remain null. Computed/unchanged forecasts
  require complete daily coverage; unchanged scenarios equal baseline. Scenarios
  are ordered, nonnegative and distinguish latent from servable demand.
- Movement recommendations reject mandatory failed/unknown checks and missing
  comparison outcomes or cost. The options engine must still generate the full
  required check set, validate policy, size allocation and shared resources, and rank
  scenarios. DTO validation does not authorize approval or dispatch. Informational
  options can retain `outcomes=null`.
- Trace steps store validated tool arguments and artifact references, never raw
  internal reasoning. Module parameter schemas are captured here; their application
  to configuration and runtime status transitions belong to PLT-04.

Post-G0 changes follow `docs/PLAN.md` §2: optional additive fields only, platform
review, regenerated producer fixtures and web types. G0 still requires the A/B/D
team reviews and merge; automated review does not freeze the contracts by itself.
