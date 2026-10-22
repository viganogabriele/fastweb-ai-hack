# Integration evidence relations

`int.dedup` runs after `int.link` and writes only `EvidenceRelation` artifacts. It
does not remove or edit documents, observations or quantities. It reads the current
run through the repository and validates each quote against its document version
and segment before relating facts.

- `duplicates`: identical facts/quotes in an exact body resend with matching sender
  and business date (or identical source hash), or an exact quoted fact with an
  explicit parent document. A forward flag, sender, product link or thread alone
  does not establish a copy.
- `possibly_same_episode`: compatible store/product/type with overlapping or
  unknown periods. Different quantities and negation do not establish independence.
  Keep both facts; do not add their quantities. Known disjoint periods remain
  separate episodes.
- `supersedes` / `retracts`: an explicit replacement or withdrawal in the fact's
  own unquoted evidence, with exactly one compatible fact in its explicit parent
  document. Known periods, product scope and units must match. Recognition currently
  covers a conservative set of Italian/English phrases; unresolvable correction
  targets, negation, hypothetical statements and questions produce an abstention
  and a degraded result. Only affirmative supported statements can suppress facts.
  Withdrawals must name the report/fact as their direct object, optionally qualified
  by its product and matching count/unit; withdrawing an objection or another
  product's report does not withdraw the fact. Unsupported object wording abstains.
  Other wording/languages remain separate observations for human verification.

Every relation retains endpoint versions, evidence references and all inspected
input artifacts. Availability is the maximum of those inputs, including the new
correction's availability, rather than its historical event date. The relation is
therefore invisible to earlier snapshots. Repeated execution is idempotent.
Segments resolve through the observation's versioned input references, and entity
links apply only to the exact observation version they reference. Missing or
ambiguous version pins abstain; a newer version never silently replaces a pin.
Certain copies are resolved before correction intent. Resending a correction or
withdrawal creates a duplicate relation, without a new correction or refreshed age.

The pure `state_at` helper demonstrates the consumer rules: union only certain
copies; choose the earliest member as the representative and keep its original
period/availability for age; apply corrections only when their endpoint versions
and relation are visible; suppress all copies of a corrected target. Withdrawal
statements are not new demand, and correction chains do not revive earlier facts.
Possible overlaps mark active representatives as non-additive. No quantity is
summed or imputed. Document count and origin-group count remain distinct; groups
are provenance groups, not statistically independent demand observations.

Downstream modules consume the contract artifacts through the repository, following
these rules; they must not import another module or treat absent overlap relations
as proof that unknown episodes are independent. The helper's dataclasses are local
views, not new persisted contracts.
