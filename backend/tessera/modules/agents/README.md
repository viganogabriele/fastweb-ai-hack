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
