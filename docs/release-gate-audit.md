# Core release gate evidence audit (REL-01a)

## Snapshot and conclusion

Audited `origin/main`: **`f5cb0cbc010a3e28bb41c16c1fb6b68287c95293`**, fetched on
2026-10-23 (audit date; dataset “today” remains **2026-10-22**). The audit branch starts
from that exact commit. References below describe that snapshot, not later main or an
eventual release candidate. Scope: [#226](https://github.com/viganogabriele/fastweb-ai-hack/issues/226),
[PLAN §4](PLAN.md#4-phases), RFC §6.2 and §7.3.

Existing tests provide substantial deterministic coverage of all ten RFC §7.3 items,
but **do not establish G3**. In particular, literal voice-disable coverage and the complete
recorded Core replay are not demonstrated here. Integrated acceptance remains with
[#115](https://github.com/viganogabriele/fastweb-ai-hack/issues/115); final candidate
revalidation, prediction export, fingerprints, human review and freeze remain with
[#211](https://github.com/viganogabriele/fastweb-ai-hack/issues/211).

RFC §6.2 rejects a fixture replacement as proof of the Core gate. No freeze tag,
hold-out evaluation, model recording, public release or certification was performed.
Only this document is changed. No secrets, hidden answers or hold-out source files
were inspected for this audit; no dataset or fixture builder was executed.

## Evidence classes

- **Pure/fixture:** inline records, scripted models, mock HTTP transports and temporary
  databases test code enforcement. A `mode="live"` RunSpec in a test does not make its
  scripted responses real model evidence.
- **Partial dev graph:** real approved MIL01 sources pass through multiple real modules,
  with extraction replaced by a fake model. This is stronger than isolated units but
  excludes the full investigator/actions/approval/API/UI path.
- **Recorded model on fixtures:** committed provider recordings replay through the real
  investigator adapter on frozen fixture cases. These are real recorded model responses,
  not real source ingestion or a complete integrated scenario.
- **Integrated candidate:** the approved dev Core path and offline rebuild from empty
  projections, including reports/traces/decisions/system inputs and API/UI isolation.
  No such candidate execution is claimed by this audit; pending #115 and #211.

## RFC §7.3 assertion map

Paths are repository-relative links; test names are pytest selectors within each file.
Assertions and limitations are specific to the audited SHA.

### 1. T1 → T2 correction → T1; no future retrieval/cache/report/tool state

[core/test_gate_temporal.py](../backend/tests/core/test_gate_temporal.py):
`test_scenario_exercises_the_correction_cases_overlay_context_and_reports` proves the
correction actually creates a `supersedes` relation and the runs publish cases, context,
computed overlays and reports. `test_t1_t2_t1_restores_the_first_state_and_leaks_nothing_of_t2`
asserts identical normalized artifacts, module results and extraction requests for both
T1 runs; all artifact/ERP availability is ≤ T1; T2 document IDs/text are absent; reports
retain T1. This is the **partial dev graph**, with `FakeLLM` and linking LLM disabled.

[core/test_repo.py](../backend/tests/core/test_repo.py)::`test_t1_t2_t1_correction_does_not_leak`
also checks repository correction visibility. [core/test_llm.py](../backend/tests/core/test_llm.py)::
`test_run_binding_isolates_as_of_and_reuses_same_snapshot_across_run_ids` asserts equivalent
snapshots reuse cache, future `as_of` changes the key, and replay constructs no provider;
`test_run_scope_versions_and_provenance_isolate_recordings` tests scope changes.
These are synthetic cache tests. Full past-run investigator retrieval/tools and recorded
report/trace replay still need integrated candidate evidence.

### 2. Disable voice; remove only its evidence and consequences

`test_switching_a_source_off_removes_only_its_consequences` in
[core/test_gate_temporal.py](../backend/tests/core/test_gate_temporal.py) disables
**`src.external`**, not voice. It asserts no ContextEvent/reference survives, the same
case IDs remain, exactly context-derived versions disappear, other artifacts differ only
by context provenance/hash, and other module results stay equal. Shared DB reruns test
stale-run isolation. [core/test_orchestrator.py](../backend/tests/core/test_orchestrator.py)::
`test_disabled_required_dependency_blocks_and_optional_dependency_degrades` checks graph policy.

**Gap:** these establish generic source disabling, not literal `src.voice` consequences.
[sources/test_voice.py](../backend/tests/modules/sources/test_voice.py)::
`test_a_note_sent_after_as_of_is_not_read` tests voice availability, not on/off equivalence.
#211 must require a voice-on/off rerun on the actual candidate (recorded ASR or explicitly
declared manual fallback), with no stale cases, references or downstream quantities.

### 3. Copies/forwards, independent requests and uncertain origins

[integration/test_gate_dedup.py](../backend/tests/modules/integration/test_gate_dedup.py)
tests the pure dedup → cases → overlay chain:
`test_copy_adds_no_units_and_does_not_renew_decay` asserts one origin, unchanged validity,
6 units rather than 12, identical scenarios and decay anchor;
`test_late_forward_of_an_expired_report_does_not_revive_it` keeps the expired episode at
baseline. `test_distinct_new_request_is_kept_and_renews_the_case` preserves both refs and
two origins; `test_distinct_new_request_alone_is_quantified_from_its_own_units` uses its own
3 units. `test_uncertain_origin_is_flagged_and_never_summed` retains both non-additive
refs and an unchanged overlay with `overlapping_episodes`. No recorded extraction accuracy
or integrated correction-to-decision claim follows from these synthetic examples.

### 4. Ambiguous identity/size, absent stock and unknown checks block movement

[actions/test_gate_blocking.py](../backend/tests/modules/actions/test_gate_blocking.py):
`test_ambiguous_product_blocks_moves_and_asks_the_store`,
`test_unidentified_size_blocks_moves_and_asks_the_store`,
`test_missing_donor_stock_record_blocks_moves_and_asks_for_verification`,
`test_unavailable_destination_stock_blocks_moves_and_asks_for_verification`, and
`test_unknown_netting_check_blocks_moves_and_asks_for_verification` exercise the relevant
branches. Shared `assert_blocked` requires informational options, the expected follow-up,
no recommended movement and mandatory blocking checks; forcing recommendation fails DTO
validation. `test_ambiguous_case_stays_in_the_queue_through_cases_and_options` persists two
cases, produces zero recommended transfers and keeps follow-ups. This uses synthetic ERP
and mock systems responses, not a UI acceptance run.

### 5. Stock conservation; late arrivals cannot recover lost sales

[actions/test_simulation.py](../backend/tests/modules/actions/test_simulation.py)::
`test_rfc_7_3_test_5_conservation` asserts stock 2, demands `[1,1,1]` → `(served,lost,ending)`
`(2,1,0)` with daily lost `[0,0,1]` and conservation. `test_late_arrival_does_not_recover_lost_sale`
retains lost 1 after a later arrival of 5 and ends at 5. Pure numeric coverage; no feasibility
or real-system stock claim.

### 6. Size totals, missing curves, zero/missing forecast, closure and partial horizon

[intelligence/test_gate_sizes.py](../backend/tests/modules/intelligence/test_gate_sizes.py):
`test_per_size_demand_adds_up_to_the_colour_demand` checks daily sums;
`test_lost_units_over_the_sizes_equal_the_colour_demand_when_nothing_is_on_hand` checks
scenario lost totals 7/14/21. `test_missing_curve_blocks_every_size_estimate_and_asks_the_store`
requires unknown curve checks, absent transfer estimates and an ask-store recommendation.
`test_zero_forecast_is_a_zero_baseline_and_missing_forecast_is_not_estimable` distinguishes
zero, missing and NaN; `test_baseline_module_keeps_zero_and_missing_apart` checks persisted DTOs.
`test_closed_days_are_zero_and_the_week_is_spread_over_open_days_only` checks 12 units over
six open days; `test_partial_week_takes_only_the_horizon_days_never_the_whole_week` checks
14 units over the selected horizon. `test_horizon_beyond_the_vintage_is_not_estimable_not_truncated`
and `test_options_refuse_a_forecast_that_covers_only_part_of_the_horizon` reject missing
coverage. These are pure/module checks over synthetic inputs, not measured forecasts.

### 7. Concurrent approvals, idempotency, stale options and optional dispatch

[actions/test_approval_gate.py](../backend/tests/modules/actions/test_approval_gate.py)::
`test_independent_approvers_cannot_reserve_the_same_last_unit` uses independent processes
and SQLite engines released at `BEGIN IMMEDIATE`: statuses `[200,409]`, one pending unit
and one draft; retrying the loser fails with `recompute` while the immutable proposal remains.
`test_same_idempotency_key_from_independent_processes_returns_one_draft` returns identical
drafts and one reservation. `test_key_collision_between_different_commands_never_overwrites_a_decision`
rejects a conflicting command; `test_independent_scenarios_do_not_share_the_single_unit_ledger`
checks namespaces. `test_local_draft_and_retries_never_attempt_optional_network_dispatch`
asserts zero HTTP attempts and `dispatch_status="draft"`.
This is real DB concurrency with synthetic inputs. Optional dispatch is disabled; timeout →
unknown reconciliation is **not exercised**, and no successful external dispatch is claimed.

### 8. Missed cutoff versus missed required-by; no future cost/delay

[actions/test_gate_cutoffs.py](../backend/tests/modules/actions/test_gate_cutoffs.py)::
`test_lane_missed_cutoff_rolls_to_next_pickup_and_required_by_decides` keeps the same next
pickup but asserts `on_time=True` versus `False`. `test_options_keep_a_move_whose_next_pickup_is_still_in_time`
recommends transfer; `test_options_block_a_move_whose_next_pickup_misses_the_horizon`
fails `eta_in_time` and recommends a follow-up. Calendar tests distinguish a remaining
feasible deadline from no remaining required-by slot.
`test_lane_cost_reviewed_after_as_of_is_not_read` returns `lane_reviewed_after_as_of`;
`test_observed_delays_are_not_read` leaves ETA unchanged.
`test_past_replay_is_unchanged_by_data_published_later` loads later synthetic ERP data,
then asserts identical past options/input hashes and excludes new costs. Synthetic
repository/module replay and mock HTTP; no real systems recording is proved.

### 9. Exhaustible budget, hostile instructions and correctly cited wrong-store numbers

[agents/test_runtime.py](../backend/tests/modules/agents/test_runtime.py)::
`test_tool_call_budget_is_really_exhausted` permits six model calls and no seventh;
`test_tool_calls_beyond_budget_in_one_turn_are_recorded_not_executed`,
`test_turn_budget_counts_retries` and `test_time_budget_and_request_timeout_shrink` cover
overflow, retries and deadline enforcement. [agents/test_investigator.py](../backend/tests/modules/agents/test_investigator.py)::
`test_hostile_document_cannot_override_checks_or_extend_agent_budget` feeds a validated
hostile quote to a scripted model: forbidden booking fails, failed/unknown checks remain,
six calls exhaust the budget and fallback is verify with no option. This demonstrates
server enforcement, **not measured real-model resistance to injection**.
`test_correct_donor_stock_number_cannot_be_published_as_destination_stock` exposes a real
fixture donor fact to the scripted model, accepts its citation, but replaces the forged
destination prose with safe verification text; persisted trace contains no forged number.
This tests investigator quantitative rendering, not a live model or the whole UI.

### 10. Empty projections, network off, cache miss, report/trace and public privacy

[core/test_replay_demo.py](../backend/tests/core/test_replay_demo.py)::
`test_repeatable_fixture_rebuild_starts_empty_and_retains_shared_inputs` asserts two isolated
fixture rebuilds have equal output/snapshot hashes. `test_product_mode_identity_is_preserved_while_client_is_forced_to_replay`
checks an empty product repo but uses a synthetic callback.
`test_swallowed_cache_miss_still_fails_and_shared_cache_is_unchanged` fails even when a module
swallows ReplayMiss; network/DNS/subprocess denial tests fail attempted escape.
`test_recorded_response_is_replayed_without_modifying_shared_cache` uses an artificial
response written by the test, not a provider recording. Voice-input rebuild checks also
use synthetic audio/transcript inputs. These establish replay boundaries, not complete Core replay.

[fixtures/test_ag03b.py](../backend/tests/fixtures/test_ag03b.py)::
`test_replay_reproduces_the_recorded_trace` matches both committed model traces (ignoring
random ID and step duration), with a provider factory that fails if constructed.
`test_different_evidence_leads_to_different_checks` requires stock/lane/options checks for D1,
clarification for the ambiguous case, no fallback/errors, and no approval/booking. This is
**recorded model on frozen fixture inputs**, with lanes explicitly unknown; it does not
replace #115's recorded source-to-report/trace/decision rebuild.

[web/scripts/test_public_demo.py](../web/scripts/test_public_demo.py)::
`test_private_metadata_identifiers_media_and_mapping_never_enter_public_files`,
`test_voice_and_raw_recordings_are_excluded`,
`test_unicode_repeated_quote_and_all_references_survive_sanitisation` and
`test_deterministic_files_and_hashes` cover synthetic builder output privacy, citations,
offsets and determinism. No actual final public bundle, deployed download routes or media
exposure audit was executed. Final bundle review remains with #129.

## Executed validation

All commands ran in this isolated worktree against the snapshot above, without live API calls.

1. `make setup`: passed, installing locked backend/web/OpenAPI dependencies.
2. `cd backend && uv run pytest -q tests/core/test_gate_temporal.py -x --tb=short`:
   **3 passed**. Additional failure-isolation runs of `tests/api/test_clarification_answers.py`
   and `tests/api/test_clarifications.py` passed **33** and **6** tests respectively.
3. Focused invariant suite below: **220 passed in 24.92s**.

```sh
cd backend && uv run pytest -q \
  tests/core/test_gate_temporal.py tests/core/test_repo.py tests/core/test_llm.py \
  tests/modules/integration/test_gate_dedup.py tests/modules/actions/test_gate_blocking.py \
  tests/modules/actions/test_simulation.py tests/modules/intelligence/test_gate_sizes.py \
  tests/modules/actions/test_approval_gate.py tests/modules/actions/test_gate_cutoffs.py \
  tests/modules/agents/test_runtime.py tests/modules/agents/test_investigator.py \
  tests/core/test_replay_demo.py tests/fixtures/test_ag03b.py
```

4. Initial `make check`: ruff and format passed; pytest reported **2 failed, 1636 passed,
   101 errors**. Setup traces showed SQLite `disk I/O error` in shared `/tmp/pytest-of-gabriele`
   while creating test databases. The root cause of the transient filesystem error is not
   established. No product fix was made based on this run.
5. Diagnostic `cd backend && uv run pytest -q -x --tb=short`: **1739 passed in 111.57s**.
   Full `make check` retry with a dedicated temporary root: **passed**. Ruff passed,
   **177 files** were already formatted, pytest **1739 passed in 109.74s**, web lint and
   TypeScript passed, **75 web tests** passed, and OpenAPI regeneration left no type diff.

```sh
mkdir -p /tmp/fastweb-rel-01a-229
TMPDIR=/tmp/fastweb-rel-01a-229 make check
```

`git diff --check` passed. A selector cross-check confirmed that all **57** explicitly named
test functions in this document exist in the audited test files. The successful reruns do
not erase the initial filesystem failure or establish its cause.

## Gaps, existing ownership and release handoff

Duplicate searches (`gh issue list --state all --search ...`) for `voice source disabling`,
`TST-02`, `TST-09` and `public bundle`, plus inspection of #115/#211/#182, found existing
ownership: closed #117 supplies generic source-disable coverage; #115 owns integrated
Core/replay; #211 explicitly owns remaining gate invariants and candidate revalidation;
#129 owns the actual public bundle. No competing implementation or duplicate issue was opened.

Before G3, #211 must bind this map to the actual candidate SHA and rerun `make check`,
obtain #115's approved dev input/cache manifests and offline evidence, verify literal
voice disabling and all downstream consequences, and review the final public bundle under
#129. Keep optional dispatch disabled unless separately implemented and verified. Any new
owner-lane defect discovered during those executions needs duplicate search and a concrete
regression issue. #227's protocol and the existing eval/placebo work are separate deliverables;
this audit neither runs hold-out evaluation nor reports accuracy, uplift or lead-time results.
