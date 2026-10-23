import { useState } from 'react'
import { Mic, Quote } from 'lucide-react'
import data from '../demo/voiceStore.json'
import { messages } from '../i18n'
import { PageHeader } from '../shell'
import { Select, StatusBadge } from '../ui'
import './voiceStore.css'

const t = messages.voice
const time = (instant: string) => new Date(instant).toLocaleTimeString('it-IT', { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit' })
const day = (instant: string) => new Date(instant).toLocaleDateString('it-IT', { timeZone: 'Europe/Rome', day: 'numeric', month: 'long', year: 'numeric' })
type Fact = { type: string; product: string | null; sku: string | string[] | null; quote: string; colour?: string; size?: string; reason?: string; caveat?: string }
const byNote = data.facts.by_note as Record<string, Fact[]>
const products = data.products as Record<string, { name: string; image: string | null; reference_name: string; source_url: string }>

function FactView({ fact }: { fact: Fact }) {
  const skus = fact.sku === null ? [] : Array.isArray(fact.sku) ? fact.sku : [fact.sku]
  return <li className="sd-voice__fact">
    <div className="sd-voice__fact-main">
      <span className="sd-voice__label">{t.types[fact.type as keyof typeof t.types]}</span>
      <h3>{fact.product ?? t.types.operativo}{fact.size && ` · taglia ${fact.size}`}{fact.colour && ` · ${fact.colour}`}</h3>
      {Array.isArray(fact.sku) && <strong className="sd-voice__warning">{t.ambiguous}</strong>}
      <blockquote><Quote aria-hidden="true" /><mark>{fact.quote}</mark></blockquote>
      {fact.caveat && <p className="sd-voice__warning">{fact.caveat}</p>}
      {skus.map(sku => <div className="sd-voice__sku" key={sku}><code>{sku}</code> · {products[sku].name}</div>)}
    </div>
    {skus.length > 0 && <div className="sd-voice__photos">
      {skus.filter(sku => products[sku].image).map(sku => <a key={sku} href={products[sku].source_url} target="_blank" rel="noreferrer" aria-label={`${products[sku].name} · ${sku} · riferimento Valentino`}>
        <img src={products[sku].image!} alt={`${products[sku].reference_name} · riferimento visivo per ${sku}`} loading="lazy" />
      </a>)}
    </div>}
  </li>
}

export function VoiceStorePage() {
  const [storeId, setStoreId] = useState(data.stores[0].store_id)
  const store = data.stores.find(item => item.store_id === storeId)!
  const notes = data.notes.filter(note => note.store_id === storeId)
  const reasons = notes.flatMap(note => byNote[note.note_id].filter(fact => fact.type === 'provato_non_comprato' && fact.reason).map(fact => ({ fact, author: note.author })))
  const conflicts = data.conflicts.filter(conflict => conflict.store_id === storeId)
  const overlap = data.overlap as { store_id: string; sku: string; authors: string[] }[]
  const common = overlap.filter(group => group.store_id === storeId)
  return <div className="sd-voice">
    <PageHeader title={`${t.title} · ${storeId} ${store.name} · ${t.evening} ${day(notes[0].sent_at)}`} subtitle={t.subtitle}
      actions={<Select label={t.store} value={storeId} options={data.stores.map(item => ({ value: item.store_id, label: `${item.store_id} · ${item.name}` }))} onValueChange={setStoreId} />} />
    <div className="sd-voice__notice">
      <StatusBadge tone="warning" label={t.badge} />
      <p>{t.disclaimer}</p><small>{t.curated}</small>
    </div>
    <div className="sd-voice__layout">
      <section aria-labelledby="voice-notes" className="sd-voice__notes">
        <h2 id="voice-notes"><Mic aria-hidden="true" />{t.notes}</h2>
        {notes.map(note => <article className="sd-voice__card" key={note.note_id}>
          <header className="sd-voice__employee">
            <div><span className="sd-voice__label">{t.pseudonym}</span><h2>{note.author}</h2></div>
            <p><time dateTime={note.sent_at}>{time(note.sent_at)}</time> · {note.duration_s.toLocaleString('it-IT')} s · {note.language}</p>
          </header>
          <details className="sd-voice__transcript"><summary>{t.transcript}</summary><p>{note.transcript}</p></details>
          <ul className="sd-voice__facts">{byNote[note.note_id].map((fact, i) => <FactView key={i} fact={fact} />)}</ul>
        </article>)}
      </section>
      <aside className="sd-voice__panels" aria-label={t.comparison}>
        <section className="sd-voice__panel"><h2>{t.onlyVoice}</h2><p>{t.onlyVoiceDescription}</p><p className="sd-voice__muted">{t.noEmail}</p>
          <ul>{reasons.map(({ fact, author }) => <li key={fact.quote}><strong>{fact.reason}</strong><p>{fact.product} · {author}</p><q>{fact.quote}</q></li>)}</ul>
        </section>
        <section className="sd-voice__panel sd-voice__panel--warning"><h2>{t.conflicts}</h2>
          {conflicts.length ? conflicts.map(conflict => <div className="sd-voice__conflict" key={conflict.sku}>
            <h3>{products[conflict.sku].name} · taglia {conflict.size}</h3>
            <p>{t.employeeSays} «{conflict.quote}» · {t.stockSays} {new Date(`${conflict.snapshot_date}T12:00:00Z`).toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit' })} dice <strong>{conflict.on_hand} {t.stock}, {conflict.in_transit} {t.transit}</strong> · <strong>{t.verify}</strong></p>
            <details><summary>{t.stockSource}</summary><code>{conflict.provenance.file}</code><pre>{conflict.provenance.row}</pre></details>
          </div>) : <p>{t.noConflicts}</p>}
        </section>
        <section className="sd-voice__panel"><h2>{t.overlap}</h2>
          {common.length ? <ul>{common.map(group => <li key={group.sku}>{products[group.sku]?.name ?? group.sku} · {group.authors.join(', ')}</li>)}</ul> : <p>{t.noOverlap}</p>}
          {notes.length === 1 && <p className="sd-voice__muted">{t.singleNote}</p>}
        </section>
      </aside>
    </div>
    <footer className="sd-voice__footer"><p>{t.photo}</p><a href={`/store/record?store=${encodeURIComponent(storeId)}`}><Mic aria-hidden="true" />{t.record}</a></footer>
  </div>
}
