import { useEffect, useState } from 'react'
import { readApi } from '../api/client'
import type { DocumentDetail } from '../api/client'
import { answerDocumentMatches, answerDocumentPath, clarificationSelectionKey, clarificationStatus, clarificationTimestamp, requestClarification, requestClarifications } from '../api/caseClarifications'
import type { Clarification, ClarificationRef, ClarificationSelection, ClarificationState } from '../api/caseClarifications'
import { Button, StatusBadge } from '../ui'
import './CaseClarificationsPanel.css'

export function CaseClarificationsPanel(props: ClarificationSelection) {
  return <ClarificationsRequest key={clarificationSelectionKey(props)} {...props} />
}
function ClarificationsRequest(props: ClarificationSelection) {
  const [state, setState] = useState<ClarificationState<Clarification[]>>({ status: 'loading' })
  const [selected, select] = useState<ClarificationRef | null>(null)
  const [revision, retry] = useState(0)
  useEffect(() => requestClarifications(props, readApi, setState), [props, revision])
  return <section className="sd-case-analysis__clarifications" aria-label="Chiarimenti pubblicati">
    <h4>Chiarimenti pubblicati</h4>
    <StatusBadge tone={props.fixtureMode ? 'warning' : 'neutral'} label={props.fixtureMode ? 'Namespace fixture · dati dimostrativi' : 'Snapshot prodotto · API'} />
    <p>Run {props.runId} · caso {props.item.id} · versione {props.item.version}</p>
    <p>Consultazione delle domande memorizzate. Gli stati non attestano l’invio di messaggi reali e non modificano run, forecast o stock.</p>
    <ReadState state={state} retry={() => { select(null); retry(value => value + 1) }} />
    {state.status === 'ready' && <>
      <ul>{state.data.map(record => <li key={JSON.stringify([record.id, record.version])}>
        <Button size="sm" variant="secondary" aria-pressed={selected?.id === record.id && selected.version === record.version} onClick={() => select({ id: record.id, version: record.version })}>
          {record.id} · {record.version} · {clarificationStatus[record.status]}
        </Button>
      </li>)}</ul>
      {selected && <ClarificationDetail key={JSON.stringify(selected)} selection={props} reference={selected} />}
    </>}
  </section>
}
function ReadState<T>({ state, retry }: { state: ClarificationState<T>; retry: () => void }) {
  if (state.status === 'ready') return null
  if (state.status === 'loading') return <p role="status">Caricamento chiarimenti…</p>
  return <div role={state.status === 'error' ? 'alert' : 'status'}><p>{state.message}</p>
    {state.status !== 'empty' && <Button size="sm" onClick={retry}>Riprova lettura</Button>}
  </div>
}
function ClarificationDetail({ selection, reference }: { selection: ClarificationSelection; reference: ClarificationRef }) {
  const [state, setState] = useState<ClarificationState<Clarification>>({ status: 'loading' })
  const [revision, retry] = useState(0)
  useEffect(() => requestClarification(selection, reference, readApi, setState), [selection, reference, revision])
  return <article aria-label="Dettaglio chiarimento">
    <ReadState state={state} retry={() => retry(value => value + 1)} />
    {state.status === 'ready' && <ClarificationRecord record={state.data} selection={selection} />}
  </article>
}
export function ClarificationRecord({ record, selection }: { record: Clarification; selection: ClarificationSelection }) {
  return <>
    <h5>{record.id} · versione {record.version}</h5>
    <StatusBadge tone="neutral" label={clarificationStatus[record.status]} />
    <p>Simulato: {record.simulated ? 'sì' : 'no'}</p>
    <p className="sd-case-clarification__text">{record.question}</p>
    <dl><dt>Timestamp domanda memorizzato</dt><dd>{clarificationTimestamp(record.asked_at)}</dd>
      <dt>Timestamp risposta memorizzato</dt><dd>{clarificationTimestamp(record.answered_at)}</dd>
      <dt>Documento risposta</dt><dd>{record.answer_document_id ?? 'Non disponibile'}</dd></dl>
    <h5>Riferimenti esatti alle osservazioni</h5>
    {record.observation_refs.length ? <ul>{record.observation_refs.map((ref, index) => <li key={index}>
      <code>{ref.kind} · {ref.id} · {ref.version}</code>
      <p>Riferimento non risolto: la navigazione diretta a questa versione dell’osservazione non è disponibile. Nessuna versione alternativa viene sostituita.</p>
    </li>)}</ul> : <p>Nessun riferimento alle osservazioni memorizzato.</p>}
    {record.answer_document_id && <AnswerDocument key={record.answer_document_id} selection={selection} id={record.answer_document_id} />}
  </>
}
function AnswerDocument({ selection, id }: { selection: ClarificationSelection; id: string }) {
  const [opened, open] = useState(false)
  const [revision, retry] = useState(0)
  const [state, setState] = useState<ClarificationState<DocumentDetail>>({ status: 'loading' })
  useEffect(() => {
    if (!opened) return
    const controller = new AbortController()
    void readApi<DocumentDetail>(answerDocumentPath(selection, id), controller.signal).then(data => {
      if (!controller.signal.aborted) setState(answerDocumentMatches(data, id) ? { status: 'ready', data }
        : { status: 'unavailable', message: 'Documento risposta non risolto nel run selezionato.' })
    }).catch(error => {
      if (!controller.signal.aborted) setState({ status: 'error', message: error instanceof Error ? error.message : 'Errore documento risposta.' })
    })
    return () => controller.abort()
  }, [selection, id, opened, revision])
  return <section aria-label="Documento risposta nello stesso run">
    <Button size="sm" variant="secondary" aria-expanded={opened} onClick={() => { setState({ status: 'loading' }); open(value => !value) }}>Documento risposta · {id}</Button>
    {opened && <><p>Ultima versione visibile nel run: il chiarimento memorizza solo l’ID del documento.</p>
      <ReadState state={state} retry={() => { setState({ status: 'loading' }); retry(value => value + 1) }} />
      {state.status === 'ready' && <><p>{state.data.document.id} · {state.data.document.version}</p><p className="sd-case-clarification__text">{state.data.document.text}</p></>}
    </>}
  </section>
}
