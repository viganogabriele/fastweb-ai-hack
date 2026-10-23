# Simulated clarification answers (OUT-02a)

`clarifications.prepare_answer` is a pure backend seam for OUT-02. It consumes a
parent RunSpec, its Case/Clarification, the exact referenced Observation and
SourceDocument versions, and a `SimulatedAnswer(text, received_at, language)`.
It returns a `PreparedAnswer`; it does not persist or schedule anything.

Pass a distinct declared `scenario_id` and a timezone-aware follow-up `as_of`.
The answer must arrive strictly after both the question and the parent clock,
and be available by the new clock. Previously published runs remain unchanged.
A cancelled/answered clarification, closed case, mismatched run/scenario/store,
missing source version or mismatched source quote is rejected as `InvalidAnswer`.
The question's `input_refs` must identify exactly the supplied Case version;
matching `case_id` alone cannot authorize a different version's lineage.

## Outputs

- A `clarification_reply` SourceDocument and one canonical Segment, with the
  answer's receipt time as availability and exact Unicode code-point offsets.
  CRLF/CR become LF; other whitespace and Unicode are preserved. The source is
  marked `simulated`, with exact clarification/observation/parent-document refs.
  Multiple document versions do not receive an arbitrary single-parent link.
  A known shared origin is retained, so a clarification does not automatically
  become an independent demand episode.
- An answered Clarification version scoped to the new scenario/run. This is a
  new object, not an update to the old published artifact.
- A follow-up RunSpec with deterministic identity and a source-manifest hash
  incorporating the answer event. Stores, module snapshots and parameters,
  config hash, code/schema version, prompt/model versions and fixture
  authorizations are preserved. No observation quantities, entity links,
  forecasts, options or approvals are inferred from the answer text.
- `seed_refs` identifies exact parent artifact versions that the integration
  must explicitly seed/remap into the new run before persisting the derived
  clarification. The complete transitive lineage must remain resolvable.

## Replay and integration boundary

Replay is the default. The trusted caller supplies `registered_answers`, an
allowlist of fingerprints previously stored with real simulated-answer events.
`answer_fingerprint(parent, clarification, answer)` computes a key; computing it
does **not** authorize an answer. Its context includes the exact parent snapshot,
question/version, text, receipt time and declared language. A miss raises
`UnrecordedAnswer`; no model or network fallback exists.

`replay=False` is the explicit live/record preparation path for a human-entered
simulated response. It still performs every scope/time check and still marks
its source as simulated. Repeated identical inputs produce identical documents,
versions and run identities; re-scheduling the same registered event at a later
clock creates a different run, not a fabricated later answer event.

OUT-02b (#167) owns durable answer storage, registry lookup, concurrency and
idempotency transactions, complete branch seeding and pipeline/API job wiring.
It must persist the source outside reconstructible run projections, register
only accepted events, and rerun extraction/linking/options in the new snapshot.
No input here is written to `generated/sources/`, and no message is sent.
