import { useEffect } from 'react'
import { EmptyState } from '../ui'
import { motion, useReducedMotion } from 'motion/react'
import { stagger, transition } from '../ui/motion'
import { messages } from '../i18n'
import './sections.css'

const appearedSections = new Set<string>()

export interface PendingSectionConfig {
  title: string
  summary: string
  endpoints: readonly string[]
  tasks: readonly string[]
}

export function PendingSection({ section }: { section: PendingSectionConfig }) {
  const reduceMotion = useReducedMotion()
  const offset = reduceMotion ? 0 : 4
  const shouldAnimate = !appearedSections.has(section.title)
  useEffect(() => { appearedSections.add(section.title) }, [section.title])
  return (
    <motion.section className="sd-pending-section" aria-label={section.title} initial={shouldAnimate ? 'hidden' : false} animate="visible" variants={{ hidden: {}, visible: { transition: { staggerChildren: stagger } } }}>
      <motion.p className="sd-pending-section__summary" variants={{ hidden: { opacity: 0, y: offset }, visible: { opacity: 1, y: 0, transition: transition.view } }}>{section.summary}</motion.p>
      <motion.div variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: transition.popover } }}>
        <EmptyState title={messages.sections.stateTitle} description={messages.sections.stateDescription} compact />
      </motion.div>
      <motion.div className="sd-pending-section__details" variants={{ hidden: {}, visible: { transition: { staggerChildren: stagger } } }}>
        <motion.div className="sd-pending-section__detail" variants={{ hidden: { opacity: 0, y: reduceMotion ? 0 : 3 }, visible: { opacity: 1, y: 0, transition: transition.view } }}>
          <h3>{messages.sections.apiLabel}</h3>
          <ul className="sd-pending-section__endpoints">
            {section.endpoints.map((endpoint) => <li key={endpoint}><code>{endpoint}</code></li>)}
          </ul>
        </motion.div>
        <motion.div className="sd-pending-section__detail" variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: transition.popover } }}>
          <h3>{messages.sections.tasksLabel}</h3>
          <ul className="sd-pending-section__tasks">
            {section.tasks.map((task) => <li key={task}><code>{task}</code></li>)}
          </ul>
        </motion.div>
      </motion.div>
    </motion.section>
  )
}
