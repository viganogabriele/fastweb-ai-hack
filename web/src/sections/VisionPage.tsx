import {
  ArrowDown, ArrowUpRight, CalendarDays, CloudSun, Database, Globe,
  Megaphone, MessagesSquare, Mic, MousePointer2, Network, Search,
  ShoppingBag, Store, Truck, UserCheck
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { fmt, messages } from '../i18n'
import { StatusBadge } from '../ui'
import './vision.css'

const t = messages.vision

type LevelCopy = {
  title: string
  description: string
  planned?: string
  destination?: string
}

function DemoBadge({ href, destination, level }: { href?: string; destination?: string; level: string }) {
  return href && destination ? (
    <a className="sd-vision__demo-link" href={href} aria-label={fmt(t.openDemo, { destination, level })}>
      <StatusBadge tone="success" label={t.demo} />
      <ArrowUpRight aria-hidden="true" />
    </a>
  ) : <StatusBadge tone="neutral" label={t.planned} />
}

function Level({ copy, icon: Icon, href, decision = false }: { copy: LevelCopy; icon: LucideIcon; href?: string; decision?: boolean }) {
  return <article className={`sd-vision__level${decision ? ' sd-vision__level--decision' : ''}`}>
    <div className="sd-vision__level-heading">
      <Icon className="sd-vision__icon" aria-hidden="true" />
      <h3>{copy.title}</h3>
      <DemoBadge href={href} destination={copy.destination} level={copy.title} />
    </div>
    <p>{copy.description}</p>
    {copy.planned && <div className="sd-vision__planned-detail">
      <span>{copy.planned}</span>
      <StatusBadge tone="neutral" label={t.planned} />
    </div>}
  </article>
}

const connectors: { id: keyof typeof t.connectors; icon: LucideIcon }[] = [
  { id: 'website', icon: MousePointer2 },
  { id: 'search', icon: Search },
  { id: 'marketing', icon: Megaphone },
  { id: 'events', icon: CalendarDays },
  { id: 'erp', icon: Database },
  { id: 'stores', icon: MessagesSquare },
  { id: 'logistics', icon: Truck }
]

export function VisionPage() {
  return <div className="sd-vision">
    <p className="sd-vision__intro">{t.intro}</p>
    <section className="sd-vision__diagram" aria-labelledby="vision-flow-title" aria-describedby="vision-flow-description">
      <header className="sd-vision__section-heading">
        <h2 id="vision-flow-title">{t.flowTitle}</h2>
        <p id="vision-flow-description">{t.flowDescription}</p>
      </header>
      <div className="sd-vision__flow">
        <Level copy={t.levels.employee} icon={Mic} href="/store/record?store=MIL01&lang=it" />
        <ArrowDown className="sd-vision__flow-arrow" aria-hidden="true" />
        <Level copy={t.levels.store} icon={Store} href="#/voce" />
        <ArrowDown className="sd-vision__flow-arrow" aria-hidden="true" />
        <Level copy={t.levels.country} icon={Globe} />
        <ArrowDown className="sd-vision__flow-arrow" aria-hidden="true" />
        <Level copy={t.levels.network} icon={Network} href="#/report" />
      </div>
      <div className="sd-vision__join" aria-hidden="true"><ArrowDown /></div>
      <section className="sd-vision__inputs" aria-labelledby="vision-inputs-title">
        <h2 id="vision-inputs-title">{t.inputsTitle}</h2>
        <div className="sd-vision__input-cards">
          {/* No Domanda online route/card exists in this branch. */}
          <Level copy={t.levels.ecommerce} icon={ShoppingBag} />
          <Level copy={t.levels.external} icon={CloudSun} href="#/pipeline" />
        </div>
      </section>
      <div className="sd-vision__join" aria-hidden="true"><ArrowDown /></div>
      <section aria-labelledby="vision-decision-title">
        <h2 id="vision-decision-title" className="sd-vision__decision-title">{t.decisionTitle}</h2>
        <Level copy={t.levels.decision} icon={UserCheck} href="#/casi" decision />
      </section>
    </section>
    <section aria-labelledby="vision-connectors-title">
      <header className="sd-vision__section-heading">
        <h2 id="vision-connectors-title">{t.connectorsTitle}</h2>
        <p>{t.connectorsDescription}</p>
      </header>
      <ul className="sd-vision__connectors">
        {connectors.map(({ id, icon: Icon }) => <li key={id} className="sd-vision__connector">
          <Icon className="sd-vision__icon" aria-hidden="true" />
          <div><h3>{t.connectors[id].title}</h3><p>{t.connectors[id].description}</p></div>
          <StatusBadge tone="neutral" label={t.planned} />
        </li>)}
      </ul>
    </section>
  </div>
}
