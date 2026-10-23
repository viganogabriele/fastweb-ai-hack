import { useEffect, useState } from 'react'
import { readApi } from '../api/client'
import { requestCaseForecast } from '../api/caseForecast'
import type { ForecastAdjustment, ForecastSelection, ForecastState } from '../api/caseForecast'
import { ChartSpline } from 'lucide-react'
import { Button, StatusBadge } from '../ui'

const units = new Intl.NumberFormat('it-IT', { maximumFractionDigits: 2 })
const fmt = (value: number | null | undefined) => value == null ? '–' : units.format(value)
// Base value up front; the low–high band only when the scenarios actually differ.
function Scenarios({ value }: { value: ForecastAdjustment['series'][number]['latent'] }) {
  if (!value) return <>–</>
  const band = fmt(value.low) !== fmt(value.high)
  return <>{fmt(value.base)}{band && <span className="sd-case-analysis__band"> {fmt(value.low)}–{fmt(value.high)}</span>}</>
}
const day = (date: string) => new Date(`${date}T00:00:00Z`).toLocaleDateString('it-IT', { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' })
const statusLabel: Record<ForecastAdjustment['status'], string> = { computed: 'corretta', unchanged: 'invariata', not_estimable: 'non stimabile' }
const ref = (r: { kind: string; id: string; version: string }) => `${r.kind} · ${r.id} · ${r.version}`

export function CaseForecastPanel(props: ForecastSelection) {
  // Include artifact inputs so even a refreshed selection cannot retain old refs.
  return <ForecastRequest key={JSON.stringify([props.runId, props.fixtureMode, props.item])} {...props} />
}
function ForecastRequest(props: ForecastSelection) {
  const [state, setState] = useState<ForecastState>({ status: 'loading' })
  const [revision, setRevision] = useState(0)
  const { item, runId, fixtureMode } = props
  useEffect(() => requestCaseForecast({ item, runId, fixtureMode }, readApi, setState), [item, runId, fixtureMode, revision])
  return <section className="sd-case-analysis__forecast" aria-label="Forecast pubblicato">
    <header className="sd-case-analysis__forecast-head">
      <h4><ChartSpline aria-hidden="true" />Previsione della domanda</h4>
      {fixtureMode && <StatusBadge tone="warning" label="Namespace fixture · dati dimostrativi" />}
    </header>
    {state.status === 'loading' ? <p role="status">Caricamento forecast…</p>
      : state.status === 'error' ? <div role="alert"><p>{state.message}</p><Button size="sm" onClick={() => setRevision((value) => value + 1)}>Riprova forecast</Button></div>
        : state.status !== 'ready' ? <p role="status">{state.message}</p>
          : <>
            {state.data.unresolved > 0 && <p role="status">Alcuni riferimenti a caso o baseline non sono risolvibili nella versione pubblicata. Nessuna versione alternativa viene sostituita.</p>}
            {!state.data.overlays.length && <p>Nessun overlay pubblicato per questa versione del caso. Le baseline non rappresentano un aggiustamento del caso.</p>}
            {state.data.baselines.map((forecast) => <ForecastRecord key={`${forecast.id}/${forecast.version}`} forecast={forecast} label="Baseline" />)}
            {state.data.overlays.map(({ forecast, baseline }) => <ForecastRecord key={`${forecast.id}/${forecast.version}`} forecast={forecast} label="Overlay del caso" unresolved={!baseline} />)}
          </>}
    <p className="sd-case-analysis__tech">{fixtureMode ? 'Fixture' : 'Snapshot API'} · run {runId} · caso {item.id} · {item.version}</p>
  </section>
}
function ForecastRecord({ forecast, label, unresolved = false }: { forecast: ForecastAdjustment; label: string; unresolved?: boolean }) {
  return <article className="sd-case-analysis__record">
    <h5>{label} <span>{day(forecast.horizon_start)} → {day(forecast.horizon_end)} · {statusLabel[forecast.status] ?? forecast.status}</span></h5>
    {forecast.reason && <p>{forecast.status === 'not_estimable' && <strong>Astensione quantitativa: </strong>}{forecast.reason}</p>}
    {unresolved && <p>La baseline referenziata non è disponibile nella versione esatta. Scenari numerici non esposti.</p>}
    {!unresolved && (forecast.series.length ? <div className="sd-case-analysis__table-wrap"><table>
      <caption className="sd-visually-hidden">{label} · unità giornaliere · scenario base, intervallo bassa–alta</caption>
      <thead><tr><th scope="col">Giorno</th><th scope="col">Baseline</th><th scope="col">Domanda latente</th><th scope="col">Servibile</th><th scope="col">Venduto</th></tr></thead>
      <tbody>{forecast.series.map((point) => <tr key={point.date}><th scope="row">{day(point.date)}</th><td>{fmt(point.baseline)}</td><td><Scenarios value={point.latent} /></td><td><Scenarios value={point.servable} /></td><td>{fmt(point.actual)}</td></tr>)}</tbody>
    </table></div> : <p>Nessun valore giornaliero pubblicato.</p>)}
    <details className="sd-case-analysis__refs">
      <summary>Riferimenti</summary>
      <dl>
        <dt>Record</dt><dd>{forecast.store_id} · {forecast.sku} · {forecast.id} · {forecast.version}</dd>
        <dt>Produttore</dt><dd>{forecast.producer} {forecast.producer_version} · origine {forecast.proposal_source}</dd>
        <dt>Vintage</dt><dd>{forecast.baseline_ref ? ref(forecast.baseline_ref) : 'Non disponibile'}</dd>
        <dt>Input</dt><dd>{forecast.input_refs.length ? forecast.input_refs.map(ref).join('; ') : 'Non disponibili'}</dd>
      </dl>
    </details>
  </article>
}
