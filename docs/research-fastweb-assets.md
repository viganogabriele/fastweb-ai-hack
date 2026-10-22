# Asset Fastweb: cosa usare nel prototipo

_Verifica documentale: 22 ottobre 2026. Non sono state effettuate chiamate autenticate ai modelli; disponibilità, latenza, quote e qualità sono ancora da misurare._

## Fonti e priorità

- **Mail «Hackathon FastwebAI – accesso ai modelli Fastweb AI Factory», 14 ottobre**, allegato `fastweb-ai-1.pdf`, pp. 1–2: modelli assegnati e accesso a FastwebAI Agents. L'originale contiene credenziali: non è copiato nel repository.
- **Kickoff Agent Forge h24, 12 ottobre**, pagina PDF 31 (slide numerata 32) per i criteri; pagina PDF 33 (slide 34) per gli strumenti: FastwebAI Agents, Romp, API/endpoint SuperPod.
- **[API Models Guide / ManagedInferenceFastweb.pdf](https://drive.google.com/file/d/14IQEKxrxzUFBeamvazCG50BZjADArdPG/view)**, collegata dalla mail e letta integralmente: p. 3 API, p. 4 modelli e hosting, pp. 5–8 tools, p. 10 embedding e trascrizione, p. 11 errori. Questa è più precisa della mail su hosting e base URL.

L'offerta pubblica MIIA/ROSS non identifica automaticamente gli strumenti assegnati al team. La [pagina pubblica MIIA](https://www.fastweb.it/grandi-aziende/artificial-intelligence/fastweb-miia/) descrive un prodotto diverso; non è il motivo per aggiungerlo alla pipeline.

## Mappa degli asset

| Asset / model ID esatto | Evidenza di disponibilità | Uso consigliato |
|---|---|---|
| `google/gemma-4-26B-A4B-it` | Mail + guida; chat, vision, tool calling; hosting **EU** nella guida | Primo candidato per estrazione e investigatore, da confrontare su un piccolo set dev. Permette un percorso con modelli dichiarati EU. |
| `Qwen/Qwen3.6-35B-A3B-FP8` | Mail + guida; chat, vision, tools; già configurato in Agents; hosting **extra-EU**, listing fino a dicembre 2026 nella guida | Alternativa pratica per la demo sintetica se passa meglio i test; adapter sostituibile. |
| `Qwen/Qwen3.5-397B-A17B-FP8` | Mail e configurazione Agents; assente dalla tabella della guida | Eventuale escalation per ambiguità difficili. Endpoint, hosting, costo/latenza non stabiliti dalla guida: non dipendere da questo modello. |
| `glm-5.3-flash` | Mail + guida; chat, vision, tools; hosting extra-EU | Alternativa da misurare; «flash» non dimostra latenza migliore sul servizio condiviso. |
| `Qwen/Qwen3.8-27B` | Mail + guida; chat, vision, tools; hosting extra-EU | Ulteriore alternativa; non fare un torneo fra tutti i modelli nelle 24 ore. |
| `Qwen/Qwen3-VL-Embedding-2B` | Mail + guida; testo e immagini; hosting EU | Matching semantico delle menzioni e retrieval delle prove. Prima testo; eventuale foto/catalogo come estensione. |
| `openai/whisper-large-v3-turbo` | Presente nella guida, non nella lista delle chiavi della mail | Audio solo se accesso confermato e utile al caso. Non aggiungerlo al percorso obbligatorio. |
| **FastwebAI Agents** | Workspace team/comune e due modelli configurati, secondo la mail | Usarlo se accelera esposizione dei tool e demo; verificare connettività al backend e supporto richiesto. API dirette come alternativa. |
| **Romp** | Elencato nel kickoff | Nessuna capacità tecnica verificata nei materiali letti: non attribuirgli funzioni e non renderlo una dipendenza. |

**Scelta proposta:** embedding Qwen + un modello chat principale. Gemma è il primo candidato documentato EU; Qwen 3.6 è un'alternativa già configurata per dati sintetici. Il 397B è un esperimento opzionale, non una prova di maggiore qualità per questo task. I ruoli sopra sono scelte progettuali, non benchmark dei modelli.

## Quattro dettagli che evitano lavoro perso

1. **Host discordanti.** La mail indica `https://spod.ai-factory.fastweb.it/v1`, ma il suo esempio curl usa `bpod1`. La guida usa `spod` in modo coerente: usarlo come configurazione iniziale e verificare l'accesso. Non concatenare due volte `/v1`.
2. **Supporto tools ≠ JSON garantito.** La guida documenta tool calling; non garantisce un particolare `response_format` con schema rigido. Validazione applicativa, un retry e poi astensione. Non assumere compatibilità completa con ogni opzione di SDK terzi.
3. **Hosting per modello.** Il marchio Fastweb sull'endpoint non implica che ogni inferenza avvenga in Italia o in UE. Per un futuro percorso EU scegliere esplicitamente modelli indicati EU e verificare anche app, log e storage. È una proprietà da verificare sull'intera configurazione, non una certificazione del prototipo.
4. **Limiti mancanti.** Non sono specificati RPM/TPM, concorrenza, budget assegnato, latenza garantita o contesto massimo per ciascun deployment. La guida descrive 429, crediti esauriti e 503: cache e replay sono necessari alla demo.

## Embedding: vantaggio concreto disponibile

La guida offre `dimensions` da 64 a 2048 (default 2048) e input testuale in batch. Iniziare a 512 e confrontare recall@5 con 2048 su menzioni ambigue; mantenere fisso il numero di candidati per un confronto leggibile. Il formato completo dell'input immagine per `/embeddings` non è mostrato: la vision chat è documentata più dettagliatamente. Non confondere disponibilità del modello con verifica del payload multimodale.

Il [report Qwen3-VL-Embedding, 2026](https://arxiv.org/abs/2601.04720) descrive retrieval multimodale e multilingua; non dimostra che un'immagine identifichi in modo certo SKU, colore e taglia. Il [repository degli autori](https://github.com/QwenLM/Qwen3-VL-Embedding) distingue embedding e reranker: il secondo non risulta assegnato dal materiale hackathon.

## Test di selezione da fare in 45–60 minuti

Confrontare **al massimo due modelli chat** su circa 20–30 note dev con negazioni, correzioni, prodotti ambigui e più lingue. Riportare JSON valido, precisione dei claim, link errati accettati, astensioni e latenza osservata. Fare almeno una chiamata tools completa andata/ritorno. Usare un set separato per le metriche finali.

Congelare la scelta e la versione del prompt dopo il test. Un piccolo campione serve a selezionare una configurazione, non a dichiarare superiorità generale o probabilità calibrate. Prevedere fallback a parsing/regole e replay chiaramente indicati.

## Valutazione: aggiornamento rispetto ai docs

Il kickoff scrive **«Allineamento tecnologico con l'infrastruttura Fastweb – peso 10%»**. `findings.md` §4 riporta invece una spiegazione orale in termini di bisogno di mercato. Le due evidenze vanno mantenute distinte: mostrare sia utilità economica sia uso effettivo degli endpoint Fastweb. I pesi 40% fattibilità e 20% innovazione agentica sono confermati dal kickoff.

Per il pitch: una traccia di chiamate reali a modello + embedding e tool di disponibilità/logistica rende l'allineamento verificabile. Non occorre usare ogni asset disponibile.
