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
  sentHint: 'La nota sarà elaborata dalla sede.',
  errors: {
    insecure: 'Il microfono richiede una connessione sicura (HTTPS). Apri il link del QR.',
    microphone: 'Microfono non disponibile o permesso negato.',
    unsupported: 'Questo browser non sa registrare audio.',
    asr: 'Trascrizione non disponibile ({status}). Puoi scrivere il testo a mano.',
    send: 'Invio non riuscito ({status}). Riprova.'
  },
  dashboard: {
    process: 'Elabora note vocali ({count})',
    running: 'Elaborazione note vocali…',
    failed: 'Elaborazione non riuscita, riprova'
  }
}
