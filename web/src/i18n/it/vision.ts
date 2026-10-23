export const vision = {
  label: 'Visione del prodotto · non sono dati del run',
  intro: 'La pipeline è fatta di moduli: ogni fonte nuova entra nello stesso formato (fatto, prova, prodotto, negozio, data) e alimenta gli stessi livelli.',
  demo: 'Nella demo',
  planned: 'Previsto',
  openDemo: 'Apri {destination}: {level}',
  flowTitle: 'Dal dipendente alla rete',
  flowDescription: 'I segnali risalgono dai negozi. La rete li unisce alla domanda online e al contesto esterno, poi li porta a chi decide.',
  inputsTitle: 'Le fonti che si uniscono alla rete',
  decisionTitle: 'La proposta torna a una persona',
  levels: {
    employee: {
      title: 'Dipendente',
      description: 'Vocale a fine turno, trascritto e rivisto dal dipendente.',
      planned: 'Domande guida per il vocale',
      destination: 'Registrazione del negozio'
    },
    store: {
      title: 'Negozio',
      description: 'Report di chiusura e verifica dei conflitti con lo stock.',
      planned: 'Confronto tra colleghi',
      destination: 'Prodotti'
    },
    country: {
      title: 'Paese e regione',
      description: 'Segnali condivisi tra negozi e divergenze da approfondire.'
    },
    network: {
      title: 'Rete',
      description: 'Priorità condivise e report per ufficio.',
      destination: 'Report'
    },
    ecommerce: {
      title: 'E-commerce',
      description: 'Richieste di riassortimento, ricerche senza risultati, esauriti online.'
    },
    external: {
      title: 'Contesto esterno',
      description: 'Meteo come fonte della pipeline.',
      planned: 'Eventi, festività, turismo e trend',
      destination: 'Pipeline'
    },
    decision: {
      title: 'Decisione',
      description: 'L’agente indaga e propone, l’umano approva una bozza.',
      destination: 'Casi'
    }
  },
  connectorsTitle: 'Connettori previsti',
  connectorsDescription: 'Nuove fonti e canali da collegare agli stessi moduli, con prove verificabili e approvazione umana prima dell’invio.',
  connectors: {
    website: { title: 'Comportamento sul sito', description: 'Carrello abbandonato, tempo sul prodotto, visualizzazioni.' },
    search: { title: 'Ricerca web e trend del momento', description: 'Segnali dal web per interpretare le richieste emergenti.' },
    marketing: { title: 'Campagne con influencer e calendario marketing', description: 'Collegare campagne e lanci alle segnalazioni dei negozi.' },
    events: { title: 'Eventi e manifestazioni in città', description: 'Contestualizzare la domanda locale con gli eventi in programma.' },
    erp: { title: 'ERP e gestionali via MCP', description: 'Consultare i sistemi aziendali attraverso connettori dedicati.' },
    stores: { title: 'Canali dei negozi: email, WhatsApp, Drive', description: 'Estendere la raccolta dei segnali dai canali usati dai negozi.' },
    logistics: { title: 'Invio approvato alla logistica', description: 'Trasmettere la proposta soltanto dopo l’approvazione umana.' }
  }
} as const
