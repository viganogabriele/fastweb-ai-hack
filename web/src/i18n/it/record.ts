// /store/record: the store's page for a live voice note (DEMO-04).
export const record = {
  eyebrow: 'Nota vocale di chiusura',
  storeLabel: 'Negozio {store}',
  noStore: 'Manca il negozio: apri la pagina dal QR del negozio (…/store/record?store=MIL01).',
  start: 'Registra',
  stop: 'Ferma',
  recording: 'In registrazione · {seconds}s',
  listening: 'Parla pure: la trascrizione compare mentre parli.',
  finalizing: 'Trascrizione finale in corso…',
  liveEmpty: 'La trascrizione apparirà qui.',
  reviewTitle: 'Controlla il testo',
  reviewHint: 'È quello che verrà letto: correggi i nomi dei capi se serve.',
  send: 'Invia nota',
  redo: 'Rifai',
  sent: 'Nota inviata',
  another: 'Registra un’altra nota',
  pending: 'Note in attesa di elaborazione: {count}',
  process: 'Elabora ora',
  processing: 'Elaborazione in corso…',
  processed: 'Elaborazione completata',
  noCases: 'Nessun caso aperto da queste note.',
  openDashboard: 'Apri nella dashboard',
  errors: {
    insecure: 'Il microfono richiede una connessione sicura (HTTPS). Apri il link del QR.',
    microphone: 'Microfono non disponibile o permesso negato.',
    unsupported: 'Questo browser non sa registrare audio.',
    asr: 'Trascrizione non disponibile ({status}). Puoi scrivere il testo a mano.',
    send: 'Invio non riuscito ({status}). Riprova.',
    process: 'Elaborazione non avviata ({status}).',
    run: 'Elaborazione terminata con stato {status}.'
  },
  caseTypes: {
    unmet_demand: 'Domanda non servita',
    stock_discrepancy: 'Discrepanza di stock',
    product_feedback: 'Feedback prodotto',
    demand_shift: 'Variazione domanda',
    traffic_change: 'Variazione traffico',
    operational_issue: 'Problema operativo',
    customer_profile: 'Profilo cliente'
  } as Record<string, string>,
  unknownScope: 'prodotto da verificare'
}
