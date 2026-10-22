import { useEffect, useState } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { Download, Search } from 'lucide-react'
import { Button } from './Button'
import { Input } from './Input'
import { Select } from './Select'
import { StatusBadge } from './StatusBadge'
import { EmptyState, LoadingState, ErrorState } from './FeedbackState'
import { formatDelta, formatDuration, formatNumber } from './format'
import { messages } from '../i18n'
import '../design/index.css'
import './Playground.css'

export function Playground() {
  const [pressed, setPressed] = useState(false)
  const [retried, setRetried] = useState(false)
  const [period, setPeriod] = useState('week')
  const [area, setArea] = useState('')
  const [source, setSource] = useState('demo')
  const [checked, setChecked] = useState(true)
  const [radio, setRadio] = useState('yes')
  const copy = messages.common.playground
  useEffect(() => { document.title = copy.title }, [copy.title])
  return (
    <main className="sd-playground">
      <h1>{copy.title}</h1>
      <p>{copy.intro}</p>
      <section className="sd-playground__section" aria-label={copy.buttons}>
        <h2>{copy.buttons}</h2>
        <div className="sd-playground__row">
          {(['primary', 'secondary', 'ghost'] as const).map(variant => (
            <Button key={variant} variant={variant} icon={<Download />}>{copy.buttonVariants[variant]}</Button>
          ))}
          <Button size="sm">{copy.compact}</Button>
          <Button icon={<Search />} iconOnly aria-label={copy.searchEvents}>{copy.searchEvents}</Button>
          <Button pressed={pressed} onClick={() => setPressed(value => !value)}>{copy.selection}</Button>
          <Button disabled>{copy.unavailable}</Button>
          <Button loading>{copy.exporting}</Button>
          <Button loading iconOnly aria-label={copy.updating}>{copy.updating}</Button>
        </div>
      </section>
      <section className="sd-playground__section" aria-label={copy.fields}>
        <h2>{copy.fields}</h2>
        <div className="sd-playground__fields">
          <Input label={copy.search} placeholder={copy.searchPlaceholder} icon={<Search />} hint={copy.nameOrId} />
          <Input label={copy.threshold} defaultValue={copy.invalidThresholdValue} hint={copy.milliseconds} error={copy.invalidNumber} />
          <Input label={copy.identifier} disabled defaultValue={copy.demoIdentifier} />
          <Input label={copy.quickFilter} hideLabel placeholder={copy.quickFilterPlaceholder} />
          <Input label={copy.search} placeholder={copy.searchPlaceholder} size="sm" />
          <Select label={copy.period} value={period} onValueChange={setPeriod} hint={copy.demoRange} options={[{ value: 'week', label: copy.last7Days }, { value: 'month', label: copy.last30Days }]} />
          <Select label={copy.area} value={area} onValueChange={setArea} error={copy.chooseAreaError} options={[{ value: '', label: copy.chooseArea, disabled: true }, { value: 'north', label: copy.north }, { value: 'south', label: copy.south }]} />
          <Select label={copy.source} value={source} onValueChange={setSource} disabled size="sm" options={[{ value: 'demo', label: copy.demoData }]} />
          <div className="sd-playground__checks">
            <label className="sd-playground__check"><input type="checkbox" checked={checked} onChange={event => setChecked(event.target.checked)} />{copy.checkbox}</label>
            <label className="sd-playground__check"><input type="radio" name="demo-radio" checked={radio === 'yes'} onChange={() => setRadio('yes')} />{copy.on}</label>
            <label className="sd-playground__check"><input type="radio" name="demo-radio" checked={radio === 'no'} onChange={() => setRadio('no')} />{copy.off}</label>
          </div>
        </div>
      </section>
      <section className="sd-playground__section" aria-label={copy.states}>
        <h2>{copy.states}</h2>
        <div className="sd-playground__row">
          <StatusBadge tone="success" label={copy.operational} count={1234} />
          <StatusBadge tone="warning" label={copy.attention} count={3} />
          <StatusBadge tone="danger" label={copy.error} />
          <StatusBadge tone="info" label={copy.analyzing} />
          <StatusBadge tone="neutral" label={copy.inactive} count={0} />
        </div>
        <EmptyState title={copy.noEvents} description={copy.changePeriod} action={<Button>{copy.resetFilters}</Button>} />
        <LoadingState label={copy.loadingEvents} lines={4} />
        {retried ? <p role="status">{copy.retryRequested}</p> : <ErrorState title={copy.dataUnavailable} description={copy.retrySoon} onRetry={() => setRetried(true)} compact />}
      </section>
      <p className="sd-num">{formatNumber(12345)} {copy.eventCount} <span>{formatDuration(1240)}</span> <span>{formatDelta(-0.013)}</span></p>
    </main>
  )
}

const root = document.getElementById('root')
if (root) {
  const hotRoot = import.meta.hot?.data.root as Root | undefined
  const reactRoot = hotRoot ?? createRoot(root)
  if (import.meta.hot) import.meta.hot.data.root = reactRoot
  reactRoot.render(<Playground />)
}
