// DEMO-03 timed rehearsal: drive the real UI through the demo click path and record a video.
//
// Needs a running demo (`make demo`, or the ports in README.md) on a fresh replay attempt:
// the decision beat writes a local draft into that attempt's database.
//
//   node rehearse.mjs --base-url http://localhost:5173 --out ../../data/demo/video/<name>
//
// Every beat is timed from the start of the recording. `--pace 1` holds each screen for the
// speaking time of docs/demo_script.md; `--pace 0.2` is a fast smoke run. The measured
// duration is the actual recording, never the sum of the targets.

import { execFileSync, spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { existsSync, mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { parseArgs } from 'node:util'
import { chromium } from 'playwright'

const here = dirname(fileURLToPath(import.meta.url))
const { values: args } = parseArgs({
  options: {
    'base-url': { type: 'string', default: 'http://localhost:5173' },
    out: { type: 'string' },
    pace: { type: 'string', default: '1' },
    slide: { type: 'string', default: join(here, 'results-slide.html') },
    reviewer: { type: 'string', default: 'Revisore demo' },
    'no-captions': { type: 'boolean', default: false },
  },
})
if (!args.out) throw new Error('--out <new directory under data/> is required')
const out = resolve(args.out)
if (existsSync(out)) throw new Error(`${out} already exists; choose a new directory`)
mkdirSync(out, { recursive: true })
const base = args['base-url'].replace(/\/$/, '')
const pace = Number(args.pace)
const size = { width: 1280, height: 800 }
const D1 = 'case-mil01-i10919b00011-20261008'
const UNKNOWN = 'case-mil01-unknown-20261009'
// Visible text that must never reach a public frame. Hits are reported, not hidden.
const DENY = [
  /valentino/i, /vlogo/i, /[\w.+-]+@[\w-]+\.[\w.]+/, /maximilian/i, /rinascente/i,
  /\b(ROM01|PAR02|LON02|ZRH01|NYC02|TYO02|SEL02|BJS01|TPE01|DXB01)\b/, /voice-token/i,
]
const DISCLOSURE = 'Dati sintetici · replay registrato offline · azioni simulate (bozze locali)'

const decided = await fetch(`${base}/api/runs/core-dev-candidate/decisions?case_id=${D1}`)
if (!decided.ok) throw new Error(`demo API not reachable at ${base}: ${decided.status}`)
if ((await decided.json()).length) {
  throw new Error(`${D1} already has a decision in this attempt: start a fresh replay attempt (README.md)`)
}

const browser = await chromium.launch()
const context = await browser.newContext({
  viewport: size,
  colorScheme: 'light',
  locale: 'it-IT',
  timezoneId: 'Europe/Rome',
  recordVideo: { dir: out, size },
})
const page = await context.newPage()
const t0 = Date.now()
const errors = []
page.on('console', (m) => m.type() === 'error' && errors.push(m.text()))
page.on('pageerror', (e) => errors.push(String(e)))

const seconds = () => (Date.now() - t0) / 1000
const hold = (s) => page.waitForTimeout(Math.round(s * pace * 1000))
const main = () => page.locator('main')

async function caption(text) {
  if (args['no-captions']) return
  await page.evaluate(
    ([line, disclosure]) => {
      let bar = document.getElementById('demo-rehearsal-caption')
      if (!bar) {
        bar = document.createElement('div')
        bar.id = 'demo-rehearsal-caption'
        bar.setAttribute('aria-hidden', 'true')
        Object.assign(bar.style, {
          position: 'fixed', left: '0', right: '0', bottom: '0', zIndex: '2147483647',
          padding: '8px 16px', background: 'rgba(20,20,20,0.86)', color: '#fff',
          font: '500 15px/1.35 Inter, system-ui, sans-serif', pointerEvents: 'none',
        })
        document.body.append(bar)
      }
      bar.innerHTML = ''
      const say = document.createElement('div')
      say.textContent = line
      const note = document.createElement('div')
      note.textContent = disclosure
      Object.assign(note.style, { fontSize: '12px', opacity: '0.75' })
      bar.append(say, note)
    },
    [text, DISCLOSURE],
  )
}

// Each hit keeps a short excerpt, so a reviewer can find it in the frames.
async function visibleTextHits() {
  const text = await page.evaluate(() => document.body.innerText)
  return DENY.flatMap((re) => {
    const match = text.match(re)
    if (!match) return []
    const at = match.index ?? 0
    return [`${re}: …${text.slice(Math.max(0, at - 40), at + 40).replace(/\s+/g, ' ')}…`]
  })
}

// Bring a section's top near the top of its scroll container (the app scrolls an inner pane,
// not the window), the way a presenter scrolls.
async function scrollTo(locator) {
  await locator.first().evaluate((el) => {
    let pane = el.parentElement
    while (pane && !(/(auto|scroll)/.test(getComputedStyle(pane).overflowY) && pane.scrollHeight > pane.clientHeight)) {
      pane = pane.parentElement
    }
    if (pane) {
      const top = el.getBoundingClientRect().top - pane.getBoundingClientRect().top + pane.scrollTop - 16
      pane.scrollTo({ top, behavior: 'smooth' })
    } else {
      window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY - 84, behavior: 'smooth' })
    }
  })
  await page.waitForTimeout(900)
}

const options = () => main().getByRole('region', { name: 'Opzioni pubblicate sul server' })
const option = (label) => options().getByRole('button', { name: new RegExp(`^${label}`) }).first()

async function openDoc(id) {
  const doc = main().getByRole('group').filter({ hasText: id })
  await doc.locator('summary').first().click()
  await main().getByText('Caricamento evidenze…').first().waitFor({ state: 'detached' })
  return doc
}

const beats = [
  {
    id: 'overview', target: '0:00-0:20', dwell: 16,
    say: 'Giovedì 22/10, sera: il run registrato offline è degraded e lo dice. 38 decisioni aperte, ordinate per priorità.',
    act: async () => {
      await page.goto(`${base}/#/panoramica`)
      await main().getByRole('heading', { name: 'Panoramica' }).waitFor()
      const toggle = main().getByRole('button', { name: 'Mostra decisioni', exact: true })
      await toggle.waitFor()
      await toggle.click()
      await main().getByRole('region', { name: 'Decisioni' }).waitFor()
    },
  },
  {
    id: 'source', target: '0:20-0:50', dwell: 22,
    say: 'Una mail di chiusura MIL01: la prova è la citazione, con offset nel testo canonico.',
    act: async () => {
      await page.getByRole('button', { name: 'Fonti', exact: true }).click()
      await page.getByRole('searchbox', { name: 'Cerca nelle fonti' }).fill('1035')
      const doc = await openDoc('doc-20261009-1035-mil01')
      const mark = doc.locator('mark').first()
      await mark.waitFor()
      await scrollTo(doc)
      await mark.hover()
    },
  },
  {
    id: 'case', target: '0:50-1:40', dwell: 35,
    say: 'Caso D1, cardigan logo M a zero: 2 documenti da 2 origini, 5 verifiche prima di decidere. Il forecast resta invariato: nessun uplift inventato.',
    act: async () => {
      await page.goto(`${base}/#/casi/${D1}/v1`)
      await main().getByRole('region', { name: 'Cosa dicono i negozi' }).waitFor()
    },
    then: async () => {
      await scrollTo(main().getByRole('region', { name: 'Forecast pubblicato' }))
      await hold(12)
    },
  },
  {
    id: 'trace', target: '1:40-2:10', dwell: 16,
    say: "L'investigatore (GLM, registrato) legge evidenze, stock e tratte; finisce il budget di 6 strumenti: fallback dichiarato, esito verify.",
    act: async () => {
      const traces = main().getByRole('region', { name: 'Tracce pubblicate' })
      await scrollTo(traces)
      await traces.getByRole('button', { name: /^Apri trace/ }).click()
      await scrollTo(traces.getByRole('article').first())
    },
    then: async () => {
      const steps = main().getByRole('region', { name: 'Tracce pubblicate' }).locator('strong')
      await scrollTo(steps.filter({ hasText: /^Passo 1 / }))
      await hold(6)
      await scrollTo(steps.filter({ hasText: /^Passo 6 / }))
      await hold(6)
    },
  },
  {
    id: 'options', target: '2:10-2:40', dwell: 16,
    say: 'Il codice calcola le opzioni. Il trasferimento da MIL02 passa i controlli ma non è consigliato: vendite perse evitate 0.',
    act: async () => {
      await scrollTo(options())
      await hold(4)
      await option('Trasferisci').click()
      await page.getByRole('dialog').getByRole('heading', { name: 'Esito atteso per scenario' }).waitFor()
    },
    then: async () => {
      await scrollTo(page.getByRole('dialog').getByRole('heading', { name: 'Controlli' }))
      await hold(8)
      await page.keyboard.press('Escape')
    },
  },
  {
    id: 'decision', target: '2:40-3:00', dwell: 13,
    say: 'Dimostrazione automatizzata del percorso di approvazione: il server salva una bozza locale simulata. Non è una nuova decisione umana; nessun invio o stock mosso.',
    act: async () => {
      await option('Avvisa il responsabile').click()
      const dialog = page.getByRole('dialog')
      await dialog.getByRole('textbox', { name: 'Il tuo nome' }).fill(args.reviewer)
      await hold(2)
      await dialog.getByRole('button', { name: 'Approva' }).click()
      await dialog.getByRole('button', { name: 'Conferma approvazione' }).waitFor()
      await hold(3)
      await dialog.getByRole('button', { name: 'Conferma approvazione' }).click()
      const journal = main().getByRole('region', { name: 'Registro dei comandi di questo caso' })
      await journal.getByText(/^Decisione salvata sul server/).waitFor({ timeout: 60_000 })
      await scrollTo(journal)
    },
  },
  {
    id: 'clarification', target: '3:00-3:25', dwell: 22,
    say: "Prodotto non identificato ('M'): resta da verificare e l'agente prepara una domanda al negozio in italiano. Bozza, mai inviata.",
    act: async () => {
      await page.goto(`${base}/#/casi/${UNKNOWN}/v1`)
      const region = main().getByRole('region', { name: 'Chiarimenti pubblicati' })
      await region.waitFor()
      await region.getByRole('button', { name: /^clarification:/ }).click()
      await scrollTo(region.getByRole('button', { name: /^clarification:/ }))
    },
  },
  {
    id: 'correction', target: '3:25-3:45', dwell: 17,
    say: "Correzione: '85,0k e non 58' sostituisce la cifra della sera (supersedes); le due cifre non vengono mai sommate.",
    act: async () => {
      await page.getByRole('button', { name: 'Fonti', exact: true }).click()
      await page.getByRole('searchbox', { name: 'Cerca nelle fonti' }).fill('20260918')
      await openDoc('doc-20260918-2115-mil01')
      const correction = await openDoc('doc-20260918-2207-mil01-corr')
      await scrollTo(correction)
    },
  },
  {
    id: 'results', target: '3:45-4:00', dwell: 12,
    say: 'La valutazione hold-out non è ancora disponibile: servono i bundle originali e il freeze approvato. Nessuna accuratezza, ROI o miglioramento dichiarato.',
    act: async () => {
      await page.goto(pathToFileURL(resolve(args.slide)).href)
    },
  },
]

const timeline = []
for (const beat of beats) {
  const start = seconds()
  await beat.act()
  await caption(beat.say)
  const hits = await visibleTextHits()
  await page.screenshot({ path: join(out, `${String(timeline.length + 1).padStart(2, '0')}-${beat.id}.png`) })
  await hold(beat.dwell)
  if (beat.then) {
    await beat.then()
    for (const hit of await visibleTextHits()) if (!hits.includes(hit)) hits.push(hit)
  }
  timeline.push({ id: beat.id, target: beat.target, start_s: start, end_s: seconds(), say: beat.say, deny_hits: hits })
  console.log(`${beat.id.padEnd(14)} ${start.toFixed(1).padStart(6)}s → ${seconds().toFixed(1).padStart(6)}s`)
}

const video = page.video()
await context.close()
await browser.close()
const webm = join(out, 'rehearsal.webm')
renameSync(await video.path(), webm)

// Playback check: ffprobe when installed; otherwise decode every frame with ffmpeg (an error
// fails the run) and read duration, codec, size and frame count from its log.
function probe(file) {
  try {
    const raw = execFileSync('ffprobe', ['-v', 'error', '-count_frames', '-show_entries', 'format=duration:stream=codec_name,width,height,nb_read_frames', '-of', 'json', file])
    const info = JSON.parse(raw)
    const stream = info.streams[0]
    return { tool: 'ffprobe', duration_s: Number(info.format.duration), codec: stream.codec_name, width: stream.width, height: stream.height, frames: Number(stream.nb_read_frames) }
  } catch (error) {
    if (error.code !== 'ENOENT') throw error
  }
  const run = spawnSync('ffmpeg', ['-hide_banner', '-xerror', '-i', file, '-map', '0:v', '-f', 'null', '-'], { encoding: 'utf8' })
  if (run.status !== 0) throw new Error(`playback decode failed for ${file}: ${run.stderr}`)
  const log = run.stderr
  const [, h, m, sec] = log.match(/Duration: (\d+):(\d+):([\d.]+)/)
  const [, codec, width, height] = log.match(/Video: (\w+).*?, (\d+)x(\d+)/)
  const frames = [...log.matchAll(/frame=\s*(\d+)/g)].at(-1)[1]
  return { tool: 'ffmpeg decode', duration_s: Number(h) * 3600 + Number(m) * 60 + Number(sec), codec, width: Number(width), height: Number(height), frames: Number(frames) }
}
const sha256 = (file) => createHash('sha256').update(readFileSync(file)).digest('hex')
const srt = (s) => new Date(s * 1000).toISOString().slice(11, 23).replace('.', ',')

// The recording runs until the browser context has closed, which can add a static tail of the
// last screen. The mp4 ends with the last beat; the raw webm is kept as recorded.
const walkthrough_s = timeline.at(-1).end_s
let mp4 = null
try {
  mp4 = join(out, 'rehearsal.mp4')
  execFileSync('ffmpeg', ['-v', 'error', '-i', webm, '-t', walkthrough_s.toFixed(2), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4])
} catch (error) {
  console.warn(`mp4 conversion skipped: ${error.message}`)
  mp4 = null
}

writeFileSync(
  join(out, 'captions.srt'),
  timeline.map((b, i) => `${i + 1}\n${srt(b.start_s)} --> ${srt(b.end_s)}\n${b.say}\n`).join('\n'),
)
const files = [webm, mp4].filter(Boolean).map((file) => ({
  file: file.slice(out.length + 1),
  sha256: sha256(file),
  playback: probe(file),
}))
const report = {
  status: 'internal_rehearsal_only',
  release_ready: false,
  release_blockers: ['Frozen hold-out evaluation and final privacy/claim review are incomplete.'],
  base_url: base,
  pace,
  captions: !args['no-captions'],
  viewport: size,
  walkthrough_s,
  wall_clock_s: seconds(),
  timeline,
  files,
  console_errors: errors,
  deny_hits: [...new Set(timeline.flatMap((b) => b.deny_hits.map((hit) => hit.split(':')[0])))],
}
writeFileSync(join(out, 'rehearsal.json'), `${JSON.stringify(report, null, 2)}\n`)
console.log(JSON.stringify({ walkthrough_s, files, console_errors: errors.length, deny_hits: report.deny_hits }, null, 2))
