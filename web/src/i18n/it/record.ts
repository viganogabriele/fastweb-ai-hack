// /store/record: the store's page for a live voice note (DEMO-04).
export const record = {
  eyebrow: 'Nota vocale di chiusura',
  storeLabel: 'Negozio {store}',
  noStore: 'Manca il negozio: apri la pagina dal QR del negozio (…/store/record?store=MIL01).',
  start: 'Registra',
  stop: 'Ferma',
  discard: 'Scarta la registrazione senza trascriverla',
  requesting: 'In attesa del permesso per il microfono…',
  retryAsr: 'Riprova trascrizione',
  recording: 'In registrazione · {seconds}s',
  finalizing: 'Trascrizione finale in corso…',
  reviewTitle: 'Controlla il testo',
  reviewHint: 'È quello che verrà letto: correggi i nomi dei capi se serve.',
  send: 'Invia nota',
  redo: 'Rifai',
  sent: 'Nota inviata',
  another: 'Registra un’altra nota',
  sentHint: 'La nota sarà elaborata dalla sede.',
  errors: {
    access: 'Manca l’accesso alla demo: apri il QR completo fornito dalla sede.',
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
