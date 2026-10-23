import { useEffect, useRef, useState } from 'react'
import type { KeyboardEvent } from 'react'
import { motion, useReducedMotion } from 'motion/react'
import type { Case } from '../api/client'
import { STORE_GEO } from './storeGeo'
import { WORLD_LAND } from './worldLand'

type Priority = Case['priority']
type Box = { x: number; y: number; w: number; h: number }

export interface MapStore {
  id: string
  total: number
  verify: number
  /** Highest priority among the store's open cases; null when it has none. */
  top: Priority | null
}

// Views on the 1000×500 equirectangular plane (see worldLand.ts). The world view crops the poles.
const REGIONS: { key: string; name: string; box: Box }[] = [
  { key: 'world', name: 'Mondo', box: { x: 0, y: 17, w: 1000, h: 395 } },
  { key: 'EMEA', name: 'Europa', box: { x: 465, y: 75, w: 150, h: 70 } },
  { key: 'AMERICAS', name: 'Americhe', box: { x: 120, y: 85, w: 230, h: 120 } },
  { key: 'APAC', name: 'Asia-Pacifico', box: { x: 740, y: 110, w: 230, h: 120 } }
]
const WORLD = REGIONS[0].box
// Close-up around a selected store, with the same proportions as the map frame.
const STORE_ZOOM = { w: 50, h: 22 }
const RANK: Record<Priority | 'none', number> = { critical: 0, high: 1, medium: 2, low: 3, none: 4 }
const PRIORITY_NAMES: Record<Priority, string> = { critical: 'critica', high: 'alta', medium: 'media', low: 'bassa' }

const project = (lat: number, lon: number) => ({ x: ((lon + 180) / 360) * 1000, y: ((90 - lat) / 180) * 500 })
const ease = (t: number) => 1 - Math.pow(1 - t, 3)

/** Slow radar pulse on stores with critical cases: the only ambient motion on the page. */
function Ping({ x, y, r, k }: { x: number; y: number; r: number; k: number }) {
  return (
    <>
      {[0, 1].map((wave) => (
        <circle
          key={wave}
          cx={x}
          cy={y}
          r={r}
          className="sd-map__ping"
          style={{ strokeWidth: 1.4 * k, transformOrigin: `${x}px ${y}px`, animationDelay: `${1.2 + wave * 1.2}s` }}
        />
      ))}
    </>
  )
}

export function StoreMap({
  stores,
  selected,
  onSelect
}: {
  stores: MapStore[]
  selected: string
  onSelect: (id: string) => void
}) {
  const reduceMotion = useReducedMotion()
  const [region, setRegion] = useState('world')
  const [box, setBox] = useState<Box>(WORLD)
  // The box being drawn, read by the next tween so a new zoom starts from where the last one is.
  const drawn = useRef<Box>(WORLD)
  const frame = useRef(0)
  useEffect(() => () => cancelAnimationFrame(frame.current), [])

  // Rendered width of the map, so markers and labels keep the same size in pixels on any screen.
  const svg = useRef<SVGSVGElement>(null)
  const [width, setWidth] = useState(760)
  useEffect(() => {
    const element = svg.current
    if (!element) return
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(1, entry.contentRect.width)))
    observer.observe(element)
    return () => observer.disconnect()
  }, [])

  // Zoom by tweening the viewBox, so the move reads as travel rather than a cut.
  const animateTo = (target: Box) => {
    cancelAnimationFrame(frame.current)
    if (reduceMotion) {
      drawn.current = target
      setBox(target)
      return
    }
    const from = drawn.current
    let start = -1
    const step = (now: number) => {
      if (start < 0) start = now
      const t = ease(Math.min(1, (now - start) / 420))
      const next = {
        x: from.x + (target.x - from.x) * t,
        y: from.y + (target.y - from.y) * t,
        w: from.w + (target.w - from.w) * t,
        h: from.h + (target.h - from.h) * t
      }
      drawn.current = next
      setBox(next)
      if (t < 1) frame.current = requestAnimationFrame(step)
    }
    frame.current = requestAnimationFrame(step)
  }
  const goTo = (key: string) => {
    setRegion(key)
    animateTo(REGIONS.find((item) => item.key === key)?.box ?? WORLD)
  }

  // Map units per screen pixel: every size below is written in pixels and multiplied by k.
  const k = box.w / width
  const placed = stores
    .map((store) => ({ store, geo: STORE_GEO[store.id] }))
    .filter((entry) => entry.geo)
    .map(({ store, geo }) => ({ store, geo, ...project(geo.lat, geo.lon) }))
    .sort((a, b) => a.store.total - b.store.total)
  const unplaced = stores.filter((store) => !STORE_GEO[store.id])

  // In the world view, stores closer than a marker's reach merge into one cluster that zooms
  // into its region on click. Zoomed views always show every store.
  type Placed = (typeof placed)[number]
  const clusters: Placed[][] = []
  for (const entry of [...placed].sort((a, b) => b.store.total - a.store.total)) {
    const near = region === 'world' ? clusters.find((group) => Math.hypot(group[0].x - entry.x, group[0].y - entry.y) < 36 * k) : undefined
    if (near) near.push(entry)
    else clusters.push([entry])
  }
  const singles = clusters.filter((group) => group.length === 1).map(([entry]) => entry).sort((a, b) => a.store.total - b.store.total)
  const groups = clusters.filter((group) => group.length > 1)
  // Entrance order: most urgent first, so the eye lands where the decisions are.
  const urgency = [...placed].sort(
    (a, b) => RANK[a.store.top ?? 'none'] - RANK[b.store.top ?? 'none'] || b.store.total - a.store.total
  )
  const delayOf = (id: string) => 0.3 + Math.max(0, urgency.findIndex((entry) => entry.store.id === id)) * 0.07
  const pop = (id: string, x: number, y: number) => ({
    initial: { scale: 0, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    transition: { type: 'spring' as const, duration: 0.5, bounce: 0.25, delay: delayOf(id) },
    style: { transformBox: 'view-box' as const, transformOrigin: `${x}px ${y}px` }
  })
  const topOf = (group: Placed[]) =>
    (['critical', 'high', 'medium', 'low'] as Priority[]).find((key) => group.some((entry) => entry.store.top === key)) ?? null

  // Selecting a store flies close enough to separate it from its neighbours; deselecting
  // returns to the store's region.
  const choose = (id: string) => {
    const geo = STORE_GEO[id]
    if (geo) {
      setRegion(geo.region)
      if (id === selected) animateTo(REGIONS.find((item) => item.key === geo.region)?.box ?? WORLD)
      else {
        const { x, y } = project(geo.lat, geo.lon)
        animateTo({ x: x - STORE_ZOOM.w / 2, y: y - STORE_ZOOM.h / 2, ...STORE_ZOOM })
      }
    }
    onSelect(id === selected ? 'all' : id)
  }
  const onKey = (event: KeyboardEvent, id: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      choose(id)
    }
  }

  return (
    <div className="sd-map">
      <div className="sd-map__regions" role="group" aria-label="Zona della mappa">
        {REGIONS.map((item) => (
          <button key={item.key} type="button" aria-pressed={region === item.key} onClick={() => goTo(item.key)}>
            {item.name}
          </button>
        ))}
      </div>
      <svg
        ref={svg}
        className="sd-map__svg"
        viewBox={`${box.x} ${box.y} ${box.w} ${box.h}`}
        preserveAspectRatio="xMidYMid meet"
        role="group"
        aria-label="Mappa dei negozi: dimensione per numero di casi aperti, colore per priorità più alta"
      >
        <defs>
          {(['critical', 'high', 'medium', 'low'] as Priority[]).map((key) => (
            <radialGradient key={key} id={`sd-map-heat-${key}`}>
              <stop offset="0%" className={`sd-map__heat-stop is-${key}`} stopOpacity="0.55" />
              <stop offset="100%" className={`sd-map__heat-stop is-${key}`} stopOpacity="0" />
            </radialGradient>
          ))}
        </defs>
        <rect x="-50" y="-50" width="1100" height="600" className="sd-map__sea" onClick={() => onSelect('all')} />
        <path d={WORLD_LAND} className="sd-map__land" style={{ strokeWidth: 0.6 * k }} />

        {placed.map(({ store, x, y }) =>
          store.top ? (
            <motion.circle
              key={`heat-${store.id}`}
              cx={x}
              cy={y}
              r={(14 + store.total * 8) * k}
              fill={`url(#sd-map-heat-${store.top})`}
              pointerEvents="none"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: delayOf(store.id) + 0.15 }}
            />
          ) : null
        )}

        {groups.map((group) => {
          const x = group.reduce((sum, entry) => sum + entry.x, 0) / group.length
          const y = group.reduce((sum, entry) => sum + entry.y, 0) / group.length
          const total = group.reduce((sum, entry) => sum + entry.store.total, 0)
          const top = topOf(group)
          const zone = REGIONS.find((item) => item.key === group[0].geo.region)
          const r = (8 + total * 0.9) * k
          const label = `${group.length} negozi vicini (${group.map((entry) => entry.store.id).join(', ')}): ${total} casi aperti. Ingrandisci ${zone?.name ?? 'la zona'}`
          return (
            <g
              key={`cluster-${group[0].store.id}`}
              className={`sd-map__store sd-map__cluster${top ? ` is-${top}` : ' is-none'}`}
              role="button"
              tabIndex={0}
              aria-label={label}
              onClick={() => goTo(group[0].geo.region)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault()
                  goTo(group[0].geo.region)
                }
              }}
            >
              <title>{label}</title>
              {top === 'critical' && <Ping x={x} y={y} r={r} k={k} />}
              <motion.g {...pop(group[0].store.id, x, y)}>
                <circle cx={x} cy={y} r={r} className="sd-map__dot" style={{ strokeWidth: 1.4 * k }} />
                <text x={x} y={y + 3.6 * k} textAnchor="middle" className="sd-map__count" style={{ fontSize: 10 * k }}>
                  {group.length}
                </text>
                <text x={x + r + 3 * k} y={y + 3.6 * k} className="sd-map__label" style={{ fontSize: 10.5 * k, strokeWidth: 2.4 * k }}>
                  {total} casi · {group.length} negozi
                </text>
              </motion.g>
            </g>
          )
        })}

        {singles.map(({ store, geo, x, y }) => {
          const r = (store.total ? 4 + store.total * 1.6 : 2.6) * k
          const isSelected = store.id === selected
          const label = `${store.id}, ${geo.name}: ${store.total} ${store.total === 1 ? 'caso aperto' : 'casi aperti'}${store.top ? `, priorità più alta ${PRIORITY_NAMES[store.top]}` : ''}${store.verify ? `, ${store.verify} da verificare` : ''}`
          return (
            <g
              key={store.id}
              className={`sd-map__store${store.top ? ` is-${store.top}` : ' is-none'}${isSelected ? ' is-selected' : ''}`}
              role="button"
              tabIndex={0}
              aria-pressed={isSelected}
              aria-label={label}
              onClick={() => choose(store.id)}
              onKeyDown={(event) => onKey(event, store.id)}
            >
              <title>{label}</title>
              {store.top === 'critical' && <Ping x={x} y={y} r={r} k={k} />}
              <motion.g {...pop(store.id, x, y)}>
                {isSelected && <circle cx={x} cy={y} r={r + 4 * k} className="sd-map__ring" style={{ strokeWidth: 1.6 * k }} />}
                <circle cx={x} cy={y} r={r} className="sd-map__dot" style={{ strokeWidth: 1.2 * k }} />
                {store.verify > 0 && <circle cx={x + r * 0.75} cy={y - r * 0.75} r={2.4 * k} className="sd-map__verify" style={{ strokeWidth: 0.8 * k }} />}
                {(store.total > 0 || region !== 'world') && (
                  <text x={x + r + 3 * k} y={y + 3.6 * k} className="sd-map__label" style={{ fontSize: 10.5 * k, strokeWidth: 2.4 * k }}>
                    {store.id}
                  </text>
                )}
              </motion.g>
            </g>
          )
        })}
      </svg>
      {unplaced.length > 0 && (
        <p className="sd-map__note">Senza coordinate, non in mappa: {unplaced.map((store) => store.id).join(', ')}.</p>
      )}
    </div>
  )
}
