import { EmptyState } from '../ui'
import { messages } from '../i18n'
import './sections.css'

export interface PendingSectionConfig {
  title: string
  summary: string
  endpoints: readonly string[]
  tasks: readonly string[]
}

export function PendingSection({ section }: { section: PendingSectionConfig }) {
  return (
    <section className="sd-pending-section" aria-label={section.title}>
      <p className="sd-pending-section__summary">{section.summary}</p>
      <EmptyState title={messages.sections.stateTitle} description={messages.sections.stateDescription} compact />
      <div className="sd-pending-section__details">
        <div className="sd-pending-section__detail">
          <h3>{messages.sections.apiLabel}</h3>
          <ul className="sd-pending-section__endpoints">
            {section.endpoints.map((endpoint) => <li key={endpoint}><code>{endpoint}</code></li>)}
          </ul>
        </div>
        <div className="sd-pending-section__detail">
          <h3>{messages.sections.tasksLabel}</h3>
          <ul className="sd-pending-section__tasks">
            {section.tasks.map((task) => <li key={task}><code>{task}</code></li>)}
          </ul>
        </div>
      </div>
    </section>
  )
}
