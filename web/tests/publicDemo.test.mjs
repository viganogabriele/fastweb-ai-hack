import assert from 'node:assert/strict'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { test } from 'node:test'

test('public demo builder preserves privacy, references and Unicode offsets', () => {
  const root = fileURLToPath(new URL('../../', import.meta.url))
  const python = fileURLToPath(new URL('../../backend/.venv/bin/python', import.meta.url))
  const result = spawnSync(python, ['-m', 'unittest', 'discover', '-s', 'web/scripts', '-p', 'test_public_demo.py', '-v'], {
    cwd: root, encoding: 'utf8', timeout: 30000
  })
  assert.equal(result.error, undefined)
  assert.equal(result.status, 0, result.stdout + result.stderr)
})
