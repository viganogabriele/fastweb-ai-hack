import { createElement, useEffect, useState } from 'react'
import type { Ref } from 'react'
import type { LucideIcon } from 'lucide-react'
import {
  AlarmClock, ArrowDown, ArrowLeft, ArrowUp, CalendarRange, CircleCheck, CloudSun, FileSpreadsheet, FileText, Flame,
  HelpCircle, History, Mail, MessageCircle, MessageSquareReply, MessageSquareWarning, Mic, Minus, PackageX, Quote,
  Server, Store, ThumbsDown, ThumbsUp, TrendingDown, TrendingUp, TriangleAlert, Users
} from 'lucide-react'
import { motion } from 'motion/react'
import { readApi } from '../api/client'
import type { Case, DocumentDetail, SourceDocument } from '../api/client'
import { Button, stagger, transition } from '../ui'
import { CaseDetailAnalysis } from './CaseDetailAnalysis'
import { caseQuotes } from './caseEvidence'
import type { CaseQuote } from './caseEvidence'
import { languageLabel, ownerLabel, shortDate, shortDay } from './caseLabels'
import { uncertaintyReasons } from './caseUtils'
import { deadline } from './overviewLogic'
import { productLinker } from './productsData'
import type { ProductCatalog } from './productsData'
import { caseStatuses, caseTypeLabel } from './productView'
import { STORE_GEO } from './storeGeo'
import { useRunData } from './useRunData'
import './caseDetail.css'

const priorities: Record<Case['priority'], { label: string; icon: LucideIcon }> = {
  critical: { label: 'Critica', icon: Flame },
  high: { label: 'Alta', icon: ArrowUp },
  medium: { label: 'Media', icon: Minus },
  low: { label: 'Bassa', icon: ArrowDown }
}
const caseIcons: Record<string, LucideIcon> = {
  unmet_demand: TrendingUp, demand_up: TrendingUp, demand_shift: TrendingUp, demand_down: TrendingDown,
  stockout: PackageX, low_stock: PackageX, stock_discrepancy: PackageX
}
const channels: Record<SourceDocument['source_type'], { label: string; icon: LucideIcon }> = {
  email: { label: 'Email di chiusura', icon: Mail },
  voice_note: { label: 'Nota vocale', icon: Mic },
  chat_message: { label: 'Chat', icon: MessageCircle },
  report: { label: 'Report', icon: FileSpreadsheet },
  external_feed: { label: 'Dato esterno', icon: CloudSun },
  system_api: { label: 'Sistema', icon: Server },
  clarification_reply: { label: 'Risposta a un chiarimento', icon: MessageSquareReply }
}
const Glyph = ({ icon }: { icon: LucideIcon }) => createElement(icon, { 'aria-hidden': true })

type Quotes = { status: 'loading' | 'ready' | 'error'; items: CaseQuote[] }

/** Verified quotes for the case, from the documents of its store (all stores for a network case). */
function useCaseQuotes(runId: string, item: Case): Quotes {
  const key = `${runId}/${item.id}/${item.version}`
  const [state, setState] = useState<Quotes & { key: string }>({ key: '', status: 'loading', items: [] })
  useEffect(() => {
    const controller = new AbortController()
    const base = `/runs/${encodeURIComponent(runId)}/documents`
    readApi<SourceDocument[]>(base, controller.signal)
      .then((documents) => Promise.all(documents
        .filter((document) => !item.store_id || document.meta.store_id === item.store_id)
        .map((document) => readApi<DocumentDetail>(`${base}/${encodeURIComponent(document.id)}`, controller.signal))))
      .then((details) => { if (!controller.signal.aborted) setState({ key, status: 'ready', items: caseQuotes(item, details) }) })
      .catch(() => { if (!controller.signal.aborted) setState({ key, status: 'error', items: [] }) })
    return () => controller.abort()
  }, [runId, item, key])
  return state.key === key ? state : { status: 'loading', items: [] }
}

export function CaseDetail({ item, runId, asOf, fixtureMode, onReturn, headingRef }: {
  item: Case
  runId: string
  asOf: string
  fixtureMode: boolean
  onReturn: () => void
  headingRef: Ref<HTMLHeadingElement>
}) {
  const catalog = useRunData<ProductCatalog>(runId, 'products')
  const quotes = useCaseQuotes(runId, item)
  const link = catalog.data ? productLinker(catalog.data)(item.scope_level, item.scope_id) : undefined
  const colour = link?.sku ? link.product.colours.find((entry) => entry.sku === link.sku)?.colour : undefined
  const due = deadline(item.decision_due_at, Date.parse(asOf))
  const checks = uncertaintyReasons(item)
  const priority = priorities[item.priority]
  const store = item.store_id ? STORE_GEO[item.store_id] : undefined
  const enter = (index: number) => ({
    initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 },
    transition: { ...transition.view, duration: 0.35, delay: index * stagger * 2 }
  })

  return (
    <article className={`sd-cd is-${item.priority}`} aria-labelledby="sd-case-detail-title">
      <Button variant="ghost" size="sm" icon={<ArrowLeft />} onClick={onReturn}>Torna alla coda</Button>

      <motion.header className="sd-cd__hero" {...enter(0)}>
        {link && (
          <figure className="sd-cd__photo">
            <img src={link.product.image} alt={`Foto di riferimento: ${link.product.reference.name}`} />
          </figure>
        )}
        <div className="sd-cd__head">
          <div className="sd-cd__tags">
            <span className={`sd-cd__tag is-priority is-${item.priority}`}><Glyph icon={priority.icon} />Priorità {priority.label.toLowerCase()}</span>
            <span className="sd-cd__tag"><Glyph icon={caseIcons[item.case_type] ?? MessageSquareWarning} />{caseTypeLabel(item.case_type)}</span>
            <span className={`sd-cd__tag${item.status === 'verify' ? ' is-verify' : ''}`}>{caseStatuses[item.status]}</span>
          </div>
          <h2 id="sd-case-detail-title" ref={headingRef} tabIndex={-1}>
            {link ? link.product.name : item.scope_id ?? 'Prodotto da identificare'}
          </h2>
          {(link || item.scope_id) && (
            <p className="sd-cd__product">
              {link && <>{[colour, link.product.subcategory].filter(Boolean).join(' · ')}</>}
              {item.scope_id && <span>{item.scope_id}</span>}
            </p>
          )}
          <p className="sd-cd__store">
            <Store aria-hidden="true" />
            <strong>{store?.name ?? item.store_id ?? 'Tutta la rete'}</strong>
            {store && <span>{item.store_id} · {store.city}, {store.country}</span>}
          </p>
          <p className="sd-cd__reason">{item.priority_reason}</p>
        </div>
        <aside className={`sd-cd__due is-${due.tone}`} aria-label="Scadenza della decisione">
          <AlarmClock aria-hidden="true" />
          <span className="sd-cd__due-label">{due.tone === 'none' ? 'Scadenza' : due.tone === 'past' ? 'Decisione' : 'Decidere entro'}</span>
          <strong>{due.tone === 'none' ? 'Nessuna' : due.text}</strong>
          {shortDate(item.decision_due_at) && <span className="sd-cd__due-date">{shortDate(item.decision_due_at)}</span>}
          <span className="sd-cd__owner"><Users aria-hidden="true" />{ownerLabel(item.owner)}</span>
        </aside>
      </motion.header>

      <motion.section className="sd-cd__section" aria-labelledby="sd-cd-quotes" {...enter(1)}>
        <h3 id="sd-cd-quotes"><Quote aria-hidden="true" />Cosa dicono i negozi</h3>
        {quotes.status === 'loading' ? (
          <div className="sd-cd__quote is-loading" aria-busy="true"><span /><span /></div>
        ) : quotes.items.length ? (
          <ul className="sd-cd__quotes">
            {quotes.items.map((entry) => {
              const channel = channels[entry.document.source_type] ?? channels.email
              const from = typeof entry.document.meta.store_id === 'string' ? entry.document.meta.store_id : null
              return (
                <li key={entry.key} className={`sd-cd__quote is-${entry.relation}`}>
                  <span className="sd-cd__relation">
                    <Glyph icon={entry.relation === 'supporting' ? ThumbsUp : ThumbsDown} />
                    {entry.relation === 'supporting' ? 'A favore' : 'Contro'}
                  </span>
                  <blockquote lang={entry.document.language ?? undefined}>{entry.quote}</blockquote>
                  <p className="sd-cd__quote-meta">
                    <span><Glyph icon={channel.icon} />{channel.label}</span>
                    {from && <span><Store aria-hidden="true" />{STORE_GEO[from]?.name ?? from}</span>}
                    {languageLabel(entry.document.language) && <span>in {languageLabel(entry.document.language)}</span>}
                    {shortDate(entry.document.available_at) && <span>{shortDate(entry.document.available_at)}</span>}
                  </p>
                </li>
              )
            })}
          </ul>
        ) : (
          <p className="sd-cd__muted">
            {quotes.status === 'error' ? 'Citazioni non caricate: riprova più tardi.' : 'Nessuna citazione verificata collegata a questo caso.'}
          </p>
        )}
      </motion.section>

      <motion.div {...enter(2)}>
        {checks.length ? (
          <section className="sd-cd__checks" aria-labelledby="sd-cd-checks">
            <h3 id="sd-cd-checks"><TriangleAlert aria-hidden="true" />Prima di decidere, verifica</h3>
            <ul>{checks.map((reason) => <li key={reason}>{reason}</li>)}</ul>
          </section>
        ) : (
          <p className="sd-cd__clear"><CircleCheck aria-hidden="true" />Nessuna verifica bloccante: il caso è pronto per una decisione.</p>
        )}
      </motion.div>

      <motion.dl className="sd-cd__facts" {...enter(3)}>
        <div>
          <dt><FileText aria-hidden="true" />Documenti</dt>
          <dd>{item.n_documents}</dd>
          <span>da {item.n_origin_groups === 1 ? '1 origine indipendente' : `${item.n_origin_groups} origini indipendenti`}</span>
        </div>
        <div className={item.n_unknown_origins ? 'is-warn' : ''}>
          <dt><HelpCircle aria-hidden="true" />Origini sconosciute</dt>
          <dd>{item.n_unknown_origins}</dd>
          <span>{item.n_unknown_origins ? 'potrebbero essere copie' : 'nessun dubbio sulle fonti'}</span>
        </div>
        <div>
          <dt><CalendarRange aria-hidden="true" />Periodo</dt>
          <dd className="is-text">{shortDay(item.window_start) ?? '–'} – {shortDay(item.window_end) ?? '–'}</dd>
          <span>finestra osservata dal caso</span>
        </div>
        <div>
          <dt><History aria-hidden="true" />Ultima prova</dt>
          <dd className="is-text">{shortDate(item.last_independent_evidence_at) ?? '–'}</dd>
          <span>evidenza indipendente più recente</span>
        </div>
      </motion.dl>

      <CaseDetailAnalysis item={item} runId={runId} fixtureMode={fixtureMode} />

      <details className="sd-cd__tech">
        <summary>Dettagli tecnici</summary>
        <dl>
          <dt>Caso</dt><dd><code>{item.id}</code> · {item.version} · disponibile dal {shortDate(item.available_at) ?? '–'}</dd>
          {([['A supporto', item.supporting], ['In conflitto', item.contradicting], ['Contesto', item.context_refs]] as const).map(([title, refs]) => (
            <div key={title}>
              <dt>{title}</dt>
              <dd>{refs.length ? refs.map((ref) => <code key={`${ref.kind}-${ref.id}-${ref.version}`}>{ref.kind} · {ref.id} · {ref.version}</code>) : 'Nessuno'}</dd>
            </div>
          ))}
          <dt>Fonti</dt>
          <dd>{item.source_refs.length ? item.source_refs.map((source, index) => <code key={`${source.uri}-${index}`}>{source.uri}{source.locator ? ` · ${source.locator}` : ''}</code>) : 'Nessun riferimento di fonte'}</dd>
        </dl>
      </details>
    </article>
  )
}
