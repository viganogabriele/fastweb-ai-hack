import { useState } from 'react'
import type { Case } from '../api/client'
import { Button, StatusBadge } from '../ui'
import { findCaseDetailFixture } from '../mocks/caseDetails'
import type { ActionOption } from '../mocks/caseDetails'
import { CaseClarificationsPanel } from './CaseClarificationsPanel'
import { CaseForecastPanel } from './CaseForecastPanel'
import { canDecideOption, decisionForRecord, decisionKey, optionBlockers } from './caseDecision'
import { CaseOptionsPanel } from './CaseOptionsPanel'
import { CaseTracePanel } from './CaseTracePanel'

type Props = { item: Case; runId: string; fixtureMode: boolean }
type Decision = { key: string; action: 'approved' | 'rejected' } | null

export function CaseDetailAnalysis({ item, runId, fixtureMode }: Props) {
  const detail = findCaseDetailFixture(runId, item.id, item.version, fixtureMode)
  const [decision, setDecision] = useState<Decision>(null)
  const [confirming, setConfirming] = useState<{ key: string; action: 'approved' | 'rejected' } | null>(null)
  const activeDecision = decisionForRecord(decision, runId, item.id, item.version)
  const activeConfirmation = decisionForRecord(confirming, runId, item.id, item.version)

  return <section className="sd-case-decision" aria-labelledby="sd-case-analysis-title">
    <header><div><p className="sd-case-detail__eyebrow">Analisi e proposta</p><h3 id="sd-case-analysis-title">Previsione e opzioni</h3></div>
      <StatusBadge tone={detail ? 'warning' : 'neutral'} label={detail ? 'Esempio sintetico disponibile' : 'Nessun esempio sintetico'} />
    </header>
    <CaseForecastPanel item={item} runId={runId} fixtureMode={fixtureMode} />
    <CaseOptionsPanel item={item} runId={runId} fixtureMode={fixtureMode} />
    <CaseTracePanel item={item} runId={runId} fixtureMode={fixtureMode} />
    <CaseClarificationsPanel item={item} runId={runId} fixtureMode={fixtureMode} />
    {detail ? <>
      <p className="sd-case-decision__demo-label sd-case-analysis__tech">Contesto demo fixture · run {runId} · caso {item.id} · versione {item.version}. Le opzioni seguenti sono esempi sintetici.</p>
      <section className="sd-case-analysis__options" aria-labelledby="sd-case-options-title">
        <h4 id="sd-case-options-title">Esempi sintetici: opzioni e controlli</h4>
        {detail.options.length ? detail.options.map((option) => <OptionCard key={option.id} option={option} item={item} fixtureMode={fixtureMode}
          decision={activeDecision?.key === decisionKey(runId, item.id, item.version, option.id) ? activeDecision.action : null}
          confirming={activeConfirmation?.key === decisionKey(runId, item.id, item.version, option.id) ? activeConfirmation.action : null}
          onConfirm={(action) => { setDecision({ key: decisionKey(runId, item.id, item.version, option.id), action }); setConfirming(null) }}
          onAsk={(action) => setConfirming({ key: decisionKey(runId, item.id, item.version, option.id), action })}
          onCancel={() => setConfirming(null)} />) : <p>Nessuna opzione è stata proposta per questa astensione.</p>}
      </section>
      <p className="sd-case-decision__notice" role="note">Le decisioni sono simulazioni locali per questo esempio. Non vengono inviate, salvate sul server o applicate a stock/run.</p>
    </> : <div className="sd-case-decision__empty"><strong>Contesto analitico sintetico non disponibile</strong>
      {item.blocking_uncertainties.length > 0
        ? <><p>Il caso riporta queste incertezze bloccanti:</p><ul>{item.blocking_uncertainties.map((reason) => <li key={reason}>{reason}</li>)}</ul></>
        : <p>Nessun esempio sintetico è definito per questa combinazione run/caso/versione. Forecast e opzioni del server sono mostrati separatamente qui sopra.</p>}
    </div>}
  </section>
}

function OptionCard({ option, item, fixtureMode, decision, confirming, onConfirm, onAsk, onCancel }: {
  option: ActionOption; item: Case; fixtureMode: boolean; decision: 'approved' | 'rejected' | null; confirming: 'approved' | 'rejected' | null
  onConfirm: (action: 'approved' | 'rejected') => void; onAsk: (action: 'approved' | 'rejected') => void; onCancel: () => void
}) {
  const blockers = optionBlockers(option)
  return <article className="sd-case-analysis__option"><header><div><strong>{option.kind}</strong>{option.recommended && <span> · raccomandata</span>}<p>{option.rationale}</p></div><StatusBadge tone={blockers.length ? 'warning' : 'success'} label={blockers.length ? `${blockers.length} blocchi` : 'Controlli superati'} /></header>
    <ul className="sd-case-analysis__checks">{option.checks.map((check) => <li key={check.name}><StatusBadge tone={check.status === 'pass' || check.status === 'not_applicable' ? 'success' : 'danger'} label={`${check.name}: ${check.status}`} /><span>{check.detail}{check.mandatory ? ' · obbligatorio' : ' · facoltativo'}</span></li>)}</ul>
    {blockers.length > 0 && <p className="sd-case-analysis__blockers"><strong>Bloccanti:</strong> {blockers.join('; ')}</p>}
    {decision && <p role="status">Decisione demo locale: {decision === 'approved' ? 'approvata' : 'respinta'}.</p>}
    {confirming && <div className="sd-case-decision__confirm" role="group" aria-label={`Conferma ${confirming === 'approved' ? 'approvazione' : 'rifiuto'} di ${option.kind}`}><span>Confermi questa decisione locale sull’opzione {option.id}?</span><Button size="sm" onClick={() => onConfirm(confirming)}>Conferma</Button><Button size="sm" variant="secondary" onClick={onCancel}>Annulla</Button></div>}
    <div className="sd-case-decision__actions"><Button disabled={!canDecideOption(fixtureMode, item.status, option, 'approved') || Boolean(confirming)} onClick={() => onAsk('approved')}>Approva opzione</Button><Button variant="secondary" disabled={!canDecideOption(fixtureMode, item.status, option, 'rejected') || Boolean(confirming)} onClick={() => onAsk('rejected')}>Respingi opzione</Button></div>
  </article>
}
