import { useEffect, useState } from 'react'
import { readApi } from '../api/client'
import type { ArtifactRef } from '../api/client'
import { requestCaseTrace, requestCaseTraces } from '../api/caseTraces'
import type { AgentTrace, TraceIdentity, TraceSelection, TraceState } from '../api/caseTraces'
import { Button, StatusBadge } from '../ui'

export function CaseTracePanel(props: TraceSelection) {
  return <TraceList key={JSON.stringify([props.runId, props.fixtureMode, props.item])} {...props} />
}
function TraceList(props: TraceSelection) {
  const [state, setState] = useState<TraceState<AgentTrace[]>>({ status: 'loading' })
  const [revision, setRevision] = useState(0)
  const [selected, setSelected] = useState<TraceIdentity | null>(null)
  useEffect(() => requestCaseTraces(props, readApi, setState), [props.item, props.runId, props.fixtureMode, revision])
  return <section className="sd-case-analysis__trace" aria-label="Tracce pubblicate">
    <h4>Tracce investigatore pubblicate</h4>
    <StatusBadge tone={props.fixtureMode ? 'warning' : 'neutral'} label={props.fixtureMode ? 'Namespace fixture · esempi sintetici' : 'Snapshot prodotto · API'} />
    <p>Run {props.runId} · caso {props.item.id} · versione {props.item.version}</p>
    <p>La modalità recorded descrive la registrazione; un esempio fixture o un fallback non dimostrano una scelta autonoma del modello.</p>
    <TraceStatus state={state} retry={() => { setSelected(null); setRevision((value) => value + 1) }} />
    {state.status === 'ready' && <>
      <p>Ultima versione visibile di ogni ID secondo l’ordine di pubblicazione.</p>
      <ul>{state.data.map((trace) => <li key={JSON.stringify([trace.id, trace.version])}>
        <Button size="sm" variant="secondary" aria-pressed={selected?.id === trace.id && selected.version === trace.version} onClick={() => setSelected({ id: trace.id, version: trace.version })}>Apri {trace.id} · {trace.version}</Button>
        <p>Modalità {trace.mode} · fallback {trace.fallback_used ? 'sì' : 'no'} · esito: {trace.outcome}</p>
      </li>)}</ul>
      {selected && <TraceDetail key={JSON.stringify([selected.id, selected.version])} selection={props} exact={selected} />}
    </>}
  </section>
}
function TraceDetail({ selection, exact }: { selection: TraceSelection; exact: TraceIdentity }) {
  const [state, setState] = useState<TraceState<AgentTrace[]>>({ status: 'loading' })
  const [revision, setRevision] = useState(0)
  useEffect(() => requestCaseTrace(selection, exact, readApi, setState), [selection.item, selection.runId, selection.fixtureMode, exact.id, exact.version, revision])
  return <article aria-label={`Traccia ${exact.id} versione ${exact.version}`}>
    <h5>{exact.id} · {exact.version}</h5>
    <TraceStatus state={state} retry={() => setRevision((value) => value + 1)} />
    {state.status === 'ready' && state.data.map((trace) => <TraceRecord key={JSON.stringify([trace.id, trace.version])} trace={trace} selection={selection} />)}
  </article>
}
function TraceStatus({ state, retry }: { state: TraceState<AgentTrace[]>; retry: () => void }) {
  if (state.status === 'ready') return null
  if (state.status === 'loading') return <p role="status">Caricamento tracce…</p>
  return <div role={state.status === 'error' ? 'alert' : 'status'}><p>{state.message}</p><Button size="sm" onClick={retry}>Riprova tracce</Button></div>
}
function References({ refs, selection }: { refs: ArtifactRef[]; selection: TraceSelection }) {
  return refs.length ? <ul>{refs.map((ref, index) => <li key={index}>{ref.kind} · {ref.id} · {ref.version} · {ref.kind === 'Case' && ref.id === selection.item.id && ref.version === selection.item.version ? 'caso selezionato' : 'riferimento non risolto in questa vista'}</li>)}</ul> : <p>Nessun riferimento pubblicato.</p>
}
// All stored/model-controlled strings use React text nodes. No HTML/Markdown
// renderer or URL navigation: unresolved refs retain their exact identity.
export function TraceRecord({ trace, selection }: { trace: AgentTrace; selection: TraceSelection }) {
  return <div>
    <p>Produttore {trace.producer} · {trace.producer_version} · calcolata {trace.computed_at}</p>
    <StatusBadge tone={trace.mode === 'fixture' || trace.fallback_used ? 'warning' : 'neutral'} label={`Modalità ${trace.mode} · fallback ${trace.fallback_used ? 'sì' : 'no'}`} />
    {trace.mode === 'fixture' && <p>Esempio sintetico fixture.</p>}
    <p>Esito: {trace.outcome}</p>
    <p>Token input: {trace.tokens_in ?? 'Non disponibili'} · token output: {trace.tokens_out ?? 'Non disponibili'}</p>
    <h5>Riferimenti input della traccia</h5><References refs={trace.input_refs} selection={selection} />
    {trace.steps.length ? <ol>{trace.steps.map((step, index) => <li key={index}>
      <strong>Passo {index + 1} · {step.tool}</strong><span> · durata {step.duration_ms} ms</span>
      <p>Argomenti (testo):</p><pre>{JSON.stringify(step.arguments, null, 2)}</pre>
      <p>Input:</p><References refs={step.input_refs} selection={selection} />
      <p>Output:</p><References refs={step.output_refs} selection={selection} />
      <p>Testo del risultato: non presente nel contratto pubblicato; sono disponibili solo i riferimenti sopra.</p>
      {step.error != null ? <p className="sd-case-analysis__error">Errore: {step.error}</p> : <p>Nessun errore registrato.</p>}
    </li>)}</ol> : <p>Nessun passo pubblicato.</p>}
  </div>
}
