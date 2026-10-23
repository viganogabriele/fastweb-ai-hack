// /store/record: the store's page for a live voice note (DEMO-04).
export const record = {
  eyebrow: 'Nota vocale di chiusura',
  storeLabel: 'Negozio {store}',
  noStore: 'Manca il negozio: apri la pagina dal QR del negozio (…/store/record?store=MIL01).',
  guideTitle: 'Prima di registrare, rispondi a queste domande',
  questions: [
    'Quali prodotti hanno suscitato interesse o sono stati provati senza acquisto?',
    'Che motivo ha dato il cliente? Cosa invece è una tua impressione?',
    "Quali taglie, colori o prodotti sono stati chiesti ma non c’erano?",
    'Cosa è stato ignorato o non è piaciuto? Altri episodi da segnalare?'
  ],
  keywords: ['Interesse', 'Motivi', 'Mancanze', 'Episodi'],
  guideHint: 'Nomina prodotto, colore e taglia se li sai. Se non conosci un numero, non inventarlo.',
  staffLabel: 'Il tuo codice',
  staffHint: 'usa il tuo codice, non il tuo nome',
  staffRequired: 'Per abilitare il microfono inserisci un codice valido: 1–32 lettere a–z, numeri o trattini.',
  remaining: 'ancora {time}',
  limit: 'Hai fino a 90 secondi. Segui le domande liberamente.',
  liveHint: 'Nota live per la demo · elaborata dalla sede · non fa parte del replay offline',
  provisional: 'Trascrizione automatica provvisoria',
  sentAt: 'Inviata il',
  noteLabel: 'Nota',
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
  sentHint: 'In attesa di elaborazione dalla sede',
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
