import { readFile } from 'node:fs/promises'
import { readTokens, resolveToken, cssName } from './build-tokens.mjs'

const tokens = await readTokens()
const local = await readFile(new URL('../src/design/local.css', import.meta.url), 'utf8')
// local.css has a light `:root {` block and a `:root[data-theme='dark'] {` override block.
const block = selector => local.slice(local.indexOf(selector)).split(/\n}\n/)[0]
const lightLocal = block(':root {')
const darkLocal = block(":root[data-theme='dark'] {")
let colors
function loadMode(mode) {
  colors = new Map([...tokens].filter(([, token]) => token.$type === 'color').map(([path]) => [cssName(path), resolveToken(tokens, path, new Set(), mode).hex]))
  for (const source of mode === 'dark' ? [lightLocal, darkLocal] : [lightLocal])
    for (const [, name, value] of source.matchAll(/(--sd-local-[\w-]+):\s*([^;]+);/g)) colors.set(name, value.trim())
}
loadMode('light')

function rgb(expression, seen = new Set()) {
  const variable = /^var\((--[\w-]+)\)$/.exec(expression)
  if (variable) {
    const name = variable[1]
    if (seen.has(name) || !colors.has(name)) throw new Error(`Unresolvable color: ${name}`)
    return rgb(colors.get(name), new Set([...seen, name]))
  }
  if (expression === 'transparent') return [0, 0, 0]
  if (/^#[0-9a-f]{6}$/i.test(expression)) return [1, 3, 5].map(offset => parseInt(expression.slice(offset, offset + 2), 16) / 255)
  const mix = /^color-mix\(in srgb, (.+) (\d+)%, (.+)\)$/.exec(expression)
  if (mix) {
    const first = rgb(mix[1], seen)
    const second = rgb(mix[3], seen)
    const weight = Number(mix[2]) / 100
    return first.map((channel, index) => channel * weight + second[index] * (1 - weight))
  }
  throw new Error(`Unsupported contrast color: ${expression}`)
}
function luminance(channels) {
  const linear = channels.map(channel => channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4)
  return linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722
}
function ratio(foreground, background) {
  const values = [foreground, background].map(name => luminance(rgb(`var(--sd-${name})`))).sort((a, b) => b - a)
  return (values[0] + 0.05) / (values[1] + 0.05)
}
const pairs = []
function add(fg, bg, minimum = 4.5) { pairs.push({ fg, bg, minimum }) }
for (const surface of ['canvas', 'sidebar', 'card', 'elevated']) {
  for (const text of ['primary', 'secondary', 'muted']) add(`color-text-${text}`, `color-surface-${surface}`)
}
add('color-text-on-accent', 'color-action-primary')
for (const state of ['success', 'warning', 'danger', 'info']) add(`color-state-${state}`, 'color-surface-card')
add('color-action-primary', 'color-surface-card')
for (const surface of ['card', 'canvas']) add('color-action-focus', `color-surface-${surface}`, 3)
// Resolve the color from the outline shorthand rather than assuming the ring stays cyan.
const ringColor = colors.get('--sd-local-focus-ring')?.match(/var\((--[\w-]+)\)/)?.[1]
if (!ringColor) throw new Error('Focus outline must contain a resolvable color variable')
for (const pair of pairs.filter(pair => pair.fg === 'color-action-focus')) pair.fg = ringColor.slice('--sd-'.length)
for (const surface of ['local-hover-surface', 'local-accent-subtle']) {
  for (const text of ['primary', 'secondary', 'muted']) add(`color-text-${text}`, surface)
}
for (const surface of ['local-accent-hover', 'local-accent-pressed']) add('color-text-on-accent', surface)
add('local-control-border', 'color-surface-card', 3)
add('local-control-border', 'color-action-secondary', 3)
add('local-series-2', 'color-surface-card', 3)
add('local-series-3', 'color-surface-card', 3)
add('color-state-danger', 'color-surface-canvas')
add('color-accent-signature', 'color-surface-card')
add('color-accent-signature', 'local-accent-subtle')
add('color-text-primary', 'local-accent-subtle')
console.log('| Mode | Foreground | Background | Ratio | Minimum | Result |')
console.log('| --- | --- | --- | ---: | ---: | --- |')
let failed = false
for (const mode of ['light', 'dark']) {
  loadMode(mode)
  for (const { fg, bg, minimum } of pairs) {
    const contrast = ratio(fg, bg)
    const pass = contrast >= minimum
    failed ||= !pass
    console.log(`| ${mode} | ${fg} | ${bg} | ${contrast.toFixed(2)}:1 | ${minimum}:1 | ${pass ? 'PASS' : 'FAIL'} |`)
  }
}
if (failed) process.exitCode = 1
