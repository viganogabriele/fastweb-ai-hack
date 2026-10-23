import { useState } from 'react'
import type { Case } from '../api/client'
import { Button, StatusBadge } from '../ui'
import { findCaseDetailFixture } from '../mocks/caseDetails'
import type { ActionOption, ForecastAdjustment } from '../mocks/caseDetails'
import { canDecideOption, decisionForRecord, decisionKey, optionBlockers } from './caseDecision'
import { CaseOptionsPanel } from './CaseOptionsPanel'

type Props = { item: Case; runId: string; fixtureMode: boolean }
type Decision = { key: string; action: 'approved' | 'rejected' } | null
const fmt = (value: number | null) => value === null ? '—' : new Intl.NumberFormat('it-IT', { maximumFractionDigits: 1 }).format(value)

export function CaseDetailAnalysis({ item, runId, fixtureMode }: Props) {
  const detail = findCaseDetailFixture(runId, item.id, item.version, fixtureMode)
  const [decision, setDecision] = useState<Decision>(null)
  const [confirming, setConfirming] = useState<{ key: string; action: 'approved' | 'rejected' } | null>(null)
  const activeDecision = decisionForRecord(decision, runId, item.id, item.version)
  const activeConfirmation = decisionForRecord(confirming, runId, item.id, item.version)

  return <section className="sd-case-decision" aria-labelledby="sd-case-analysis-title">
    <header><div><p className="sd-case-detail__eyebrow">Analisi e proposta</p><h3 id="sd-case-analysis-title">Previsione, traccia e opzioni</h3></div>
      <StatusBadge tone={detail ? 'warning' : 'neutral'} label={detail ? 'Esempio sintetico' : fixtureMode ? 'Fixture senza esempio' : 'Dettagli non esposti'} />
    </header>
    <CaseOptionsPanel item={item} runId={runId} fixtureMode={fixtureMode} />
    {detail ? <>
      <p className="sd-case-decision__demo-label">Contesto demo fixture · run {runId} · caso {item.id} · versione {item.version}. Tutti i valori e gli esiti seguenti sono esempi sintetici.</p>
      <ForecastView forecast={detail.forecast} />
      <section className="sd-case-analysis__trace" aria-labelledby="sd-case-trace-title">
        <h4 id="sd-case-trace-title">Traccia agente</h4><p>{detail.trace.outcome} · modalità {detail.trace.mode}{detail.trace.fallbackUsed ? ' · fallback usato' : ''}</p>
        <ol>{detail.trace.steps.map((step, index) => <li key={`${step.tool}-${index}`}>
          <strong>{step.tool}</strong><span>{step.durationMs} ms</span>
          <code>Argomenti: {JSON.stringify(step.arguments)}</code><p>{step.result}</p>{step.error && <p className="sd-case-analysis__error">Errore: {step.error}</p>}
        </li>)}</ol>
      </section>
      <section className="sd-case-analysis__options" aria-labelledby="sd-case-options-title">
        <h4 id="sd-case-options-title">Opzioni e controlli</h4>
        {detail.options.length ? detail.options.map((option) => <OptionCard key={option.id} option={option} item={item} fixtureMode={fixtureMode}
          decision={activeDecision?.key === decisionKey(runId, item.id, item.version, option.id) ? activeDecision.action : null}
          confirming={activeConfirmation?.key === decisionKey(runId, item.id, item.version, option.id) ? activeConfirmation.action : null}
          onConfirm={(action) => { setDecision({ key: decisionKey(runId, item.id, item.version, option.id), action }); setConfirming(null) }}
          onAsk={(action) => setConfirming({ key: decisionKey(runId, item.id, item.version, option.id), action })}
          onCancel={() => setConfirming(null)} />) : <p>Nessuna opzione è stata proposta per questa astensione.</p>}
      </section>
      <p className="sd-case-decision__notice" role="note">Le decisioni sono simulazioni locali per questo esempio. Non vengono inviate, salvate sul server o applicate a stock/run.</p>
    </> : <div className="sd-case-decision__empty"><strong>Dettagli analitici non disponibili</strong>
      {item.blocking_uncertainties.length > 0
        ? <><p>Il caso riporta queste incertezze bloccanti:</p><ul>{item.blocking_uncertainties.map((reason) => <li key={reason}>{reason}</li>)}</ul></>
        : <p>{fixtureMode ? 'Nessun esempio sintetico è definito per questa combinazione run/caso/versione.' : 'Il run live non pubblica forecast, tracce, opzioni o controlli tramite l’API disponibile.'}</p>}
      <p>Approve e Reject sono disabilitati perché non sono disponibili opzioni verificabili.</p>
      <div className="sd-case-decision__actions"><Button disabled>Approva</Button><Button variant="secondary" disabled>Respingi</Button></div>
    </div>}
  </section>
}

function ForecastView({ forecast }: { forecast: ForecastAdjustment }) {
  if (forecast.status === 'not_estimable') return <section className="sd-case-analysis__forecast" aria-labelledby="sd-case-forecast-title"><h4 id="sd-case-forecast-title">Baseline e scenari</h4>
    <p>Astensione quantitativa: nessuno scenario numerico viene mostrato.</p><p><strong>Motivo:</strong> {forecast.reason}</p></section>
  return <section className="sd-case-analysis__forecast" aria-labelledby="sd-case-forecast-title"><h4 id="sd-case-forecast-title">Baseline e scenari · {forecast.horizonStart} → {forecast.series.at(-1)?.date}</h4>
    {forecast.reason && <p>{forecast.reason}</p>}
    <div className="sd-case-analysis__table-wrap"><table><thead><tr><th>Giorno</th><th>Baseline</th><th>Domanda latente · bassa/base/alta</th><th>Servibile · bassa/base/alta</th></tr></thead>
      <tbody>{forecast.series.map((point) => <tr key={point.date}><th scope="row">{point.date}</th><td>{fmt(point.baseline)}</td><td>{point.latent ? `${fmt(point.latent.low)} / ${fmt(point.latent.base)} / ${fmt(point.latent.high)}` : 'Non disponibile'}</td><td>{point.servable ? `${fmt(point.servable.low)} / ${fmt(point.servable.base)} / ${fmt(point.servable.high)}` : 'Non disponibile'}</td></tr>)}</tbody>
    </table></div>
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
