# Case investigator (AG-03)

## Product scope

RFC 4.8.2 and PLAN Phase 2 define the behavior: investigate one selected, visible
case; inspect evidence and possible donor conflicts; check stock and lanes;
re-evaluate deterministic options; propose a valid option or return verify/monitor.
Clarifications are local drafts. Approval, reservations, dispatch and changes to
case quantities are outside the investigator.

## Technical decisions

- `investigator.py` exports `MANIFEST`, `run(ctx)` and the `investigate` service
  for the future PLT-12 route. Explicit `case_ids` select work; no automatic scan
  of every historical case or live provider call during discovery.
- Reuse `AgentLoop` and `model_for_run`, including the existing cache and budgets.
  Evidence comes only from this run's repository. Resolve IDs and versions in
  code, restrict SKU/location queries to the selected case and run, and reject
  unknown donor candidates before calling the shared options engine.
- Five argument-validated tools plus runtime `finish` implement RFC 4.8.2.
  The shared ACT-02 gather/evaluate service is the documented cross-module seam.
  Stock/lane reads use the existing time-filtered SystemsReader.
- Proposals and clarification drafts are buffered until the investigation finishes,
  then persisted before their trace. Deterministic IDs make unchanged drafts
  idempotent. No contract/schema changes, dependencies or migrations are needed.
- Final choices must refer to this case's freshly evaluated options. Unknown or
  failed mandatory movement checks block selection. Published explanations use
  deterministic templates, never unvalidated model quantities or causal claims.
- Fallback inspects evidence, ambiguity and already available option checks in
  that order. It does not call the provider or logistics after budget exhaustion.
- Missing recordings propagate as ReplayMiss; never present a fixture or fake
  model conversation as a real recorded trace.

## Delivery and acceptance

1. Implement the scoped tools and terminal validation; verify foreign IDs, ambiguous
   identities, unavailable stock, candidate validation and clarification idempotency.
2. Wire the service into the discovered module and persist contract-valid output;
   verify fallback, missing-recording behavior and module execution with fake clients.
3. Record two real dev conversations with different evidence/check paths, then replay
   them offline. Keep their fixture-backed input provenance explicit. This step needs
   a team-provided per-model key through Settings; no key is currently configured.
4. Run `make check`, update the PR with evidence and mark ready only after acceptance.

The specification above is complete for implementation. The user explicitly
requested implementation; work proceeds after this planning checkpoint.

## Using the implementation

The registry discovers `ag.investigator` automatically. Supply
`{"case_ids": ["<visible case ID>"]}` in its module snapshot; at most twenty cases
can be explicitly selected. It requires `int.cases` and `act.options`, and uses
`ctx.clients["llm"]` plus the existing `systems` client factory. A replay cache miss
fails the module explicitly. Missing systems data produces a degraded investigation
with unknown checks; it never becomes stock zero.

`investigate(repo, case_id, model=..., reader=..., policy=..., horizon_days=7)` is
the service seam for PLT-12. Pass a writable, transaction-bound repository from
`repo_session`; the module worker owns its transaction. Published historical runs
remain immutable: a later investigation needs its own writable job snapshot.
It returns `AgentRun` (validated choice plus persisted trace), and stores acquired
stock projections, evaluated option versions and local clarification drafts before
storing references to them. The service does not update the original case.

Clarification questions are model-generated drafts, with the store language supplied
by the repository and required by the prompt; a human still reviews their wording.
Final decision explanations are server templates, so arbitrary model numbers or
causal claims do not become the displayed rationale.

## Validation status

The automated conversations use fake models and fixture-backed dev cases. They
verify different stock/ambiguity tool paths, scoped IDs, persistence, draft
idempotency, donor-conflict gates, valid vs blocked proposals, exhausted-budget
fallback and the real LLM adapter's explicit replay-miss behavior. These tests do
**not** claim a real provider chose those tools. The two real recorded dev traces
remain blocked on a team-provisioned per-model key file; issue #81 and PR #146
must remain open/draft until those recordings can be made and replayed.
