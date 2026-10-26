import { useEffect, useRef, useState } from 'react'

/** Rendered width of an element, so SVG charts can draw in pixels instead of scaling their text. */
export function useElementWidth<T extends Element>(fallback: number, min = 240) {
  const ref = useRef<T>(null)
  const [width, setWidth] = useState(fallback)
  useEffect(() => {
    const element = ref.current
    if (!element) return
    const observer = new ResizeObserver(([entry]) => setWidth(Math.max(min, entry.contentRect.width)))
    observer.observe(element)
    return () => observer.disconnect()
  }, [min])
  return { ref, width }
}
