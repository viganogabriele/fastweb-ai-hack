# Signal Dark: implementation notes

What was built from [`IMPLEMENTATION_PROMPT.md`](IMPLEMENTATION_PROMPT.md), where to find it, and
which choices are ours. **Every value or behaviour not in [`tokens.json`](../../src/design/tokens.json)
is a local implementation decision, not a fact of the reference designs.** The references give one
inspected NexaDash frame and a text description; nothing here is "pixel-perfect".

## Map

| Area | Path | Decisions |
|---|---|---|
| Tokens (DTCG → CSS) | `src/design/tokens.json` → `scripts/build-tokens.mjs` → `src/design/tokens.css`; local tokens `src/design/local.css`; entry `src/design/index.css` | [A](decisions/A-tokens-primitives.md) |
| Primitives | `src/ui/` (Button, Input, Select, StatusBadge, Empty/Loading/ErrorState, VisuallyHidden, it-IT `format.ts`) | [A](decisions/A-tokens-primitives.md) |
| Shell | `src/shell/` (AppShell, SidebarNav, PageHeader, `useShell`) | [B](decisions/B-shell.md) |
| Widgets + demo | `src/widgets/` (FilterBar, KpiCard, ChartCard, SVG charts, MiniBar, DataTable), `src/demo/` (data, API stub, scenarios, DashboardPage) | [C](decisions/C-widgets.md) |
| Composition | `src/App.tsx` | this file |
| Plan sections | `src/sections/PendingSection.tsx`: one "waiting for backend" view per planned page (Casi, Fonti, Report, Pipeline, Prodotti, Chiarimenti), driven by `messages.sections.items` (summary, API endpoints, plan tasks) | this file |
| UI copy | `src/i18n/`: `messages` (one file per namespace in `it/`), `fmt()` for `{name}` placeholders, `LOCALE` | this file |
| Contract between lanes | [`CONTRACT.md`](CONTRACT.md) | |

Commands (from `web/`): `node scripts/build-tokens.mjs` regenerates `tokens.css` after editing
`tokens.json`; `node scripts/check-contrast.mjs` prints WCAG ratios for the pairs in use.
Component state galleries (dev only, not in the build): `/preview/a.html` (primitives),
`/preview/b.html` (shell).

## Replacing the demo data

`src/demo/api.ts` `fetchDashboard(filters, scenario)` is the only data seam; it returns a typed
`DashboardResponse` (`src/demo/data.ts`). Swap its body for a real request and drop the
`scenario` argument. The "Scenario demo" select in the top bar (`App.tsx`) only exists to show
loading / empty / error states and should go with it.

## Key decisions (summary; details in the lane files)

- **Breakpoints:** sidebar persistent ≥ 1024px, modal drawer below; dashboard grid 12 columns
  ≥ 1280px, 6 from 720px, 1 below. Chosen by rendering at 1440, 1280, 1024, 768, 390, 320px.
- **Sidebar width** 248px; drawer with focus trap, Esc/scrim close, focus return, inert background.
- **Motion:** one transition duration token, 0ms under `prefers-reduced-motion`; no decorative
  animation. **Shadow:** only on the drawer overlay; cards separate by tone + subtle border.
- **Focus ring, control height (≥ 40px), 44px hit targets, hover/selected tints, chart series
  2/3 colors, scrim:** local tokens in `local.css`, derived from semantic tokens.
- **Charts:** hand-written SVG; primary series cyan solid with round markers, comparison series
  dashed neutral, regions with fill patterns; legend with shape samples; keyboard-navigable line
  chart with a tooltip that also works on focus; text trend summary and "Mostra dati" table.
- **Table:** semantic table, sortable headers (`aria-sort`), row selection with a demo bulk
  action, intentional horizontal scroll region with preserved headers on narrow screens.
- **Announcements:** one polite page-level announcer (loading, result count, no results) and a
  single assertive alert on error; widget feedback states render without their own live roles
  (`announce={false}`).
- **Demo data:** deterministic synthetic monitoring of a fictional SaaS platform, labelled "Dati
  demo"; p95 latency computed from merged histograms with in-bin interpolation.

## Verification (2026-10-22)

- `npm run lint`, `npm run typecheck`, `npm run build` pass.
- Contrast: 32 token pairs pass WCAG AA (lowest text pair 4.93:1); rendered pairs measured in the
  browser (placeholder 7.34:1, muted metadata 7.97:1, chart axes 9.87:1).
- Headless Chromium at 1440×900, 1280×800, 1024×768, 768×1024, 390×844, 320×640: no horizontal
  page overflow, no clipped select values, checkbox targets 44×44, focused sort headers scroll
  fully into view, one announcement per state, no console errors.
- Keyboard: skip link, drawer trap/return, chart arrows/Home/End, disclosures, sort, selection.
- Manual visual comparison with the single inspected NexaDash frame: same relation between
  sidebar, KPI row, chart cards and detail; no artwork, logo or copy reused.

## Known limits

- Only "Panoramica" is a working view (synthetic demo data). The plan views (RFC §3.4) show
  what they will contain, the endpoints they will read (RFC §4.6) and the tasks they wait for; no
  fake data. The run / `as_of` selector in the top bar is a disabled placeholder until
  `GET /api/runs` exists. When a view gets its API, replace its `PendingSection` in `App.tsx`.
- No real screen-reader session (NVDA/VoiceOver) was run; announcements were checked via the DOM.
- Browser zoom was approximated with equivalent CSS viewports, not native browser-UI zoom.
- Token values are proposals from one frame; if better screenshots arrive, update `tokens.json`
  first, regenerate, then adjust components (no disconnected overrides).

## Polish pass (2026-10-23)

- **Strings:** every user-facing string, aria-label and title comes from `src/i18n/it/*.ts`; no
  literal `'it-IT'` outside `src/i18n/index.ts`. A new locale adds a sibling folder with the same
  shape.
- **Select:** custom select-only combobox (button + portalled listbox) instead of the native
  `<select>`: arrows/Home/End/typeahead, Enter/Space, Esc returns focus, Tab and outside click
  close, disabled options skipped, popover clamped to the viewport. API: `onValueChange(value)`,
  `size: 'md' | 'sm'`. Native look also removed from search inputs, checkboxes/radios, autofill,
  number spinners and scrollbars (`base.css`, `local.css`).
- **Navigation:** groups Demo / Flusso di lavoro / Approfondimenti; the section lives in the URL
  hash (`#/casi`), so views are linkable and back/forward works. Mode badge in the top bar
  (`Dati sintetici` on Panoramica, `Non disponibile` on plan views); the scenario select only
  appears on Panoramica; the run placeholder is hidden below 768px.
- **Panoramica:** compact filter toolbar, no decorative ` · ` separators, period stated once by
  the filter, update time in the page header, demo bulk action labelled as demo.
- **Verified:** lint, typecheck, build; Playwright (Chromium) at 320–1440px with no horizontal
  overflow and no console errors; keyboard select, hash back/forward, drawer navigation, error
  scenario alert.

## Motion pass (2026-10-23)

- **Library:** `motion` (`motion/react`) for enter/exit, shared elements and the drawer gesture;
  CSS transitions for hover, press, focus and colour. Shared presets in `src/ui/motion.ts`
  (custom ease-out curves, 120–300ms, springs with bounce 0), mirrored as `--sd-local-ease-*` /
  `--sd-local-duration-*` in `local.css`. `<MotionConfig reducedMotion="user">` wraps the app.
- **Where:** Select popover (origin-aware scale+fade, shorter exit); button press `scale(0.97)`;
  animated checkbox/radio marks; sidebar active indicator as a shared `layoutId`; section
  entrance (fade + 5px, no exit so there is never an empty frame); mobile drawer with
  swipe-to-dismiss (72px or 500px/s); first-load stagger of KPI and chart cards, line draw-in and
  bar growth (not on refetch); "Mostra dati" height animation; table bulk bar enter/exit.
- **Reduced motion:** movement removed everywhere, opacity kept where it carries state; skeleton
  pulse and spinner stop.
- **Not animated on purpose:** keyboard highlight in listboxes, chart keyboard navigation,
  filter changes and refetches.
