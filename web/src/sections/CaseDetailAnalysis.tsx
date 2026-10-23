import { ArrowLeftRight, ChartSpline, UserCheck } from 'lucide-react'
import type { Case } from '../api/client'
import { StatusBadge } from '../ui'
import { CaseClarificationsPanel } from './CaseClarificationsPanel'
import { CaseForecastPanel } from './CaseForecastPanel'
import { CaseOptionsPanel } from './CaseOptionsPanel'
import { CaseTracePanel } from './CaseTracePanel'

type Props = { item: Case; runId: string; fixtureMode: boolean }

// What the analysis will show once the forecast and options services publish for demo runs.
const upcoming = [
  { icon: ChartSpline, title: 'Previsione corretta', text: 'La domanda attesa nei prossimi giorni, con e senza quanto riportato dai negozi.' },
  { icon: ArrowLeftRight, title: 'Opzioni di stock', text: 'Trasferimenti o riassortimenti possibili, con i controlli già fatti dal sistema.' },
  { icon: UserCheck, title: 'La tua decisione', text: 'Approvi o respingi un’opzione: il sistema propone, decidi tu.' }
]

export function CaseDetailAnalysis({ item, runId, fixtureMode }: Props) {
  // Demo runs have no published analysis: show what is coming instead of synthetic stand-ins.
  if (fixtureMode)
    return <section className="sd-case-decision sd-case-soon" aria-labelledby="sd-case-analysis-title">
      <header>
        <div><p className="sd-case-detail__eyebrow">Analisi e proposta</p><h3 id="sd-case-analysis-title">Cosa fare con questo caso</h3></div>
        <StatusBadge tone="info" label="In arrivo" />
      </header>
      <ul className="sd-case-soon__steps">
        {upcoming.map(({ icon: Icon, title, text }) => (
          <li key={title}><span aria-hidden="true"><Icon /></span><strong>{title}</strong><p>{text}</p></li>
        ))}
      </ul>
    </section>

  return <section className="sd-case-decision" aria-labelledby="sd-case-analysis-title">
    <header><div><p className="sd-case-detail__eyebrow">Analisi e proposta</p><h3 id="sd-case-analysis-title">Previsione e opzioni</h3></div></header>
    <CaseForecastPanel item={item} runId={runId} fixtureMode={fixtureMode} />
    <CaseOptionsPanel item={item} runId={runId} fixtureMode={fixtureMode} />
    <CaseTracePanel item={item} runId={runId} fixtureMode={fixtureMode} />
    <CaseClarificationsPanel item={item} runId={runId} fixtureMode={fixtureMode} />
  </section>
}
