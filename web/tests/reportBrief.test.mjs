import test from 'node:test'
import assert from 'node:assert/strict'
import { parseBrief } from '../src/sections/reportBrief.ts'

const markdown = `# Brief by office, as of 2026-10-22 20:00 UTC

## allocation

- **MIL01 · VLOGO CARDIGAN (I10919B00011)**: open, priority high [1].
  - stockout 0 units [2]
  - unmet demand, quantity unknown [3]
  - baseline I10919B00011-742 10-23..10-29 9.8 units, unchanged [4]
  - recommended option: notify owner [5]
  - open: Stock level is the store's statement; ERP stock not checked yet.
  - something new from the template [9]
- **MIL01 · product not identified**: verify, priority medium [6].`

test('brief template lines become structured, citation indexes are zero-based', () => {
  const brief = parseBrief(markdown, 6)
  assert.equal(brief.title, 'Brief by office, as of 2026-10-22 20:00 UTC')
  assert.deepEqual(brief.sections.map((section) => [section.title, section.entries.length]), [['allocation', 2]])
  const [first, second] = brief.sections[0].entries
  assert.deepEqual([first.store, first.product, first.code, first.status, first.priority, first.citation], ['MIL01', 'VLOGO CARDIGAN', 'I10919B00011', 'open', 'high', 0])
  assert.deepEqual(first.signals, [
    { kind: 'stockout', quality: null, amount: 0, unit: 'units', citation: 1 },
    { kind: 'unmet_demand', quality: 'unknown', amount: null, unit: null, citation: 2 }
  ])
  assert.deepEqual(first.forecasts, [{ sku: 'I10919B00011-742', from: '10-23', to: '10-29', units: 9.8, status: 'unchanged', citation: 3 }])
  assert.deepEqual(first.options, [{ kind: 'notify_owner', citation: 4 }])
  assert.deepEqual(first.open, ["Stock level is the store's statement; ERP stock not checked yet."])
  assert.deepEqual([second.product, second.code, second.status, second.citation], ['product not identified', null, 'verify', 5])
})

test('unknown lines and out-of-range citations are kept as raw text, never dropped', () => {
  const [first] = parseBrief(markdown, 6).sections[0].entries
  assert.deepEqual(first.other, ['something new from the template [9]'])
  const loose = parseBrief('Preface line\n\n- not a template item', 0)
  assert.deepEqual(loose.notes, ['Preface line'])
  assert.equal(loose.sections[0].entries[0].headline, 'not a template item')
})
