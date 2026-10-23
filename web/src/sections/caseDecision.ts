export type DecisionAction = 'approved' | 'rejected'
export type CaseDecisionStatus = 'open' | 'verify' | 'monitor' | 'action_proposed' | 'decided' | 'closed'

export function canSimulateDecision(
  fixtureMode: boolean,
  status: CaseDecisionStatus,
  action: DecisionAction
) {
  if (!fixtureMode || status === 'closed' || status === 'decided') return false
  // Approving requires a published option with checks. WEB-05 has no options
  // endpoint/fixture yet; rejecting the case can still be demonstrated locally.
  return action === 'rejected'
}
