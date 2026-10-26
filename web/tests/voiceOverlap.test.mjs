import assert from 'node:assert/strict'
import test from 'node:test'
import { colleagueOverlap } from '../src/demo/voiceOverlap.ts'

const note = (author, sku, store_id = 'MIL01', size) => ({ store_id, author, facts: [{ sku, size }] })
test('distinct authors mentioning different SKUs have no overlap', () => {
  assert.deepEqual(colleagueOverlap([note('roberto', 'COAT-23R'), note('martino', 'VEST-742')]), [])
})
test('two colleagues sharing a SKU produce one overlap', () => {
  assert.deepEqual(colleagueOverlap([note('roberto', 'COAT-23R'), note('martino', 'COAT-23R')]), [
    { store_id: 'MIL01', sku: 'COAT-23R', authors: ['martino', 'roberto'] }
  ])
})
test('same author twice does not count', () => {
  assert.deepEqual(colleagueOverlap([note('roberto', 'COAT-23R'), note('roberto', 'COAT-23R')]), [])
})
test('different stores do not count', () => {
  assert.deepEqual(colleagueOverlap([note('roberto', 'COAT-23R'), note('paolo', 'COAT-23R', 'MIL02')]), [])
})
test('different sizes of the same style and colour still group', () => {
  assert.equal(colleagueOverlap([note('roberto', 'COAT-23R', 'MIL01', '2'), note('martino', 'COAT-23R', 'MIL01', '3')]).length, 1)
})
test('ambiguous candidates and operational facts cannot create agreement', () => {
  assert.deepEqual(colleagueOverlap([note('a', ['COAT-23R', 'VEST-742']), note('b', 'COAT-23R'), note('a', null), note('b', null)]), [])
})
