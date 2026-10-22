import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { resolve } from 'node:path'

export const source = new URL('../src/design/tokens.json', import.meta.url)
export const cssName = path => `--sd-${path.split('.').slice(1).join('-')}`

export async function readTokens() {
  const tree = JSON.parse(await readFile(source, 'utf8'))
  const tokens = new Map()
  function visit(node, path = []) {
    if (Object.hasOwn(node, '$value')) {
      tokens.set(path.join('.'), node)
      return
    }
    for (const [key, value] of Object.entries(node)) {
      if (!key.startsWith('$')) visit(value, [...path, key])
    }
  }
  visit(tree)
  return tokens
}

export function resolveToken(tokens, path, seen = new Set()) {
  if (!tokens.has(path)) throw new Error(`Unknown token alias: ${path}`)
  if (seen.has(path)) throw new Error(`Circular token alias: ${[...seen, path].join(' → ')}`)
  const value = tokens.get(path).$value
  if (typeof value === 'string' && /^\{.*\}$/.test(value)) {
    return resolveToken(tokens, value.slice(1, -1), new Set([...seen, path]))
  }
  return value
}

export async function buildTokens() {
  const tokens = await readTokens()
  const names = new Set()
  const declarations = []
  for (const [path, token] of tokens) {
    resolveToken(tokens, path)
    const name = cssName(path)
    if (names.has(name)) throw new Error(`Duplicate CSS token name: ${name}`)
    names.add(name)
    const value = token.$value
    let css
    if (typeof value === 'string' && /^\{.*\}$/.test(value)) css = `var(${cssName(value.slice(1, -1))})`
    else if (token.$type === 'color') css = value.hex
    else if (token.$type === 'dimension') css = `${value.value}${value.unit}`
    else if (token.$type === 'fontFamily') css = value.map(font => /\s/.test(font) ? JSON.stringify(font) : font).join(', ')
    else if (token.$type === 'fontWeight') css = String(value)
    else throw new Error(`Unsupported token type: ${path} (${token.$type})`)
    if (!css) throw new Error(`Missing CSS value: ${path}`)
    declarations.push(`  ${name}: ${css};`)
  }
  await writeFile(new URL('../src/design/tokens.css', import.meta.url), `/* generated, do not edit */\n:root {\n${declarations.join('\n')}\n}\n`)
  console.log(`Generated ${declarations.length} Signal Dark tokens`)
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await buildTokens()
