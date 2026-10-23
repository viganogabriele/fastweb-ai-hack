import { useEffect, useState } from 'react'
import { readApi } from '../api/client'
import { requestCaseForecast } from '../api/caseForecast'
import type { ForecastAdjustment, ForecastSelection, ForecastState } from '../api/caseForecast'
import { Button, StatusBadge } from '../ui'

const fmt = (value: number | null | undefined) => value == null ? 'Non disponibile' : new Intl.NumberFormat('it-IT', { maximumFractionDigits: 20 }).format(value)
const scenarios = (value: ForecastAdjustment['series'][number]['latent']) => value ? `${fmt(value.low)} / ${fmt(value.base)} / ${fmt(value.high)}` : 'Non disponibile'

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
    <h4>Baseline e scenari pubblicati</h4>
    <StatusBadge tone={fixtureMode ? 'warning' : 'neutral'} label={fixtureMode ? 'Namespace fixture · dati dimostrativi' : 'Snapshot prodotto · API'} />
    <p>Run {runId} · caso {item.id} · versione {item.version}</p>
    {state.status === 'loading' ? <p role="status">Caricamento forecast…</p>
      : state.status === 'error' ? <div role="alert"><p>{state.message}</p><Button size="sm" onClick={() => setRevision((value) => value + 1)}>Riprova forecast</Button></div>
        : state.status !== 'ready' ? <p role="status">{state.message}</p>
          : <>
            {state.data.unresolved > 0 && <p role="status">Alcuni riferimenti a caso o baseline non sono risolvibili nella versione pubblicata. Nessuna versione alternativa viene sostituita.</p>}
            {!state.data.overlays.length && <p>Nessun overlay pubblicato per questa versione del caso. Le baseline non rappresentano un aggiustamento del caso.</p>}
            {state.data.baselines.map((forecast) => <ForecastRecord key={`${forecast.id}/${forecast.version}`} forecast={forecast} label="Baseline" />)}
            {state.data.overlays.map(({ forecast, baseline }) => <ForecastRecord key={`${forecast.id}/${forecast.version}`} forecast={forecast} label="Overlay del caso" unresolved={!baseline} />)}
          </>}
  </section>
}
function ForecastRecord({ forecast, label, unresolved = false }: { forecast: ForecastAdjustment; label: string; unresolved?: boolean }) {
  return <article>
    <h5>{label} · {forecast.store_id} · {forecast.sku}</h5>
    <p>{forecast.id} · {forecast.version} · {forecast.producer} {forecast.producer_version} · origine proposta: {forecast.proposal_source}</p>
    <p>Orizzonte {forecast.horizon_start} → {forecast.horizon_end} · stato: {forecast.status}</p>
    {forecast.reason && <p><strong>{forecast.status === 'not_estimable' ? 'Astensione quantitativa' : 'Motivo'}:</strong> {forecast.reason}</p>}
    <p>Riferimento vintage: {forecast.baseline_ref ? `${forecast.baseline_ref.kind} · ${forecast.baseline_ref.id} · ${forecast.baseline_ref.version}` : 'Non disponibile'}</p>
    <p>Riferimenti input: {forecast.input_refs.length ? forecast.input_refs.map((ref) => `${ref.kind} · ${ref.id} · ${ref.version}`).join('; ') : 'Non disponibili'}</p>
    {unresolved && <p>La baseline referenziata non è disponibile nella versione esatta. Scenari numerici non esposti.</p>}
    {!unresolved && (forecast.series.length ? <div className="sd-case-analysis__table-wrap"><table>
      <caption>{label} · unità giornaliere · scenari bassa / base / alta</caption>
      <thead><tr><th scope="col">Giorno</th><th scope="col">Baseline</th><th scope="col">Domanda latente</th><th scope="col">Servibile</th></tr></thead>
      <tbody>{forecast.series.map((point) => <tr key={point.date}><th scope="row">{point.date}</th><td>{fmt(point.baseline)}</td><td>{scenarios(point.latent)}</td><td>{scenarios(point.servable)}</td></tr>)}</tbody>
    </table></div> : <p>Nessun valore giornaliero pubblicato.</p>)}
  </article>
}
