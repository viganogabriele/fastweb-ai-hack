export type DecisionAction = 'approved' | 'rejected'
export type CaseDecisionStatus = 'open' | 'verify' | 'monitor' | 'action_proposed' | 'decided' | 'closed'
import type { ActionOption } from '../mocks/caseDetails'

export function decisionKey(runId: string, caseId: string, version: string, optionId: string) {
  return `${runId}\u0000${caseId}\u0000${version}\u0000${optionId}`
}

export function decisionForRecord<T extends { key: string }>(
  decision: T | null,
  runId: string,
  caseId: string,
  version: string
) {
  return decision?.key.startsWith(`${runId}\u0000${caseId}\u0000${version}\u0000`) ? decision : null
}

export function optionBlockers(option: ActionOption) {
  return [
    ...option.blockers,
    ...option.checks
      .filter((check) => check.mandatory && check.status !== 'pass' && check.status !== 'not_applicable')
      .map((check) => `${check.name}: ${check.status === 'unknown' ? 'esito sconosciuto' : 'non superato'}`)
  ].filter((blocker, index, all) => all.indexOf(blocker) === index)
}

export function canDecideOption(
  fixtureMode: boolean,
  status: CaseDecisionStatus,
  option: ActionOption,
  action: DecisionAction
) {
  if (!fixtureMode || status === 'closed' || status === 'decided') return false
  if (action === 'rejected') return true
  return optionBlockers(option).length === 0
}
