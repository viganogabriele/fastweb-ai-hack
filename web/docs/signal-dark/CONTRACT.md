# Signal Dark: implementation contract

Shared contract for the parallel build of the Signal Dark demo dashboard in `web/`.
Design inputs: [`DESIGN.md`](DESIGN.md), [`COMPONENTS.md`](COMPONENTS.md),
[`../../src/design/tokens.json`](../../src/design/tokens.json) (DTCG, single source of truth),
[`IMPLEMENTATION_PROMPT.md`](IMPLEMENTATION_PROMPT.md) (brief and acceptance criteria).

Stack: React 19 + Vite + TypeScript (strict, `verbatimModuleSyntax`, `noUnusedLocals`), plain CSS
files co-located with components, icons from `lucide-react` (already installed). **No other
runtime dependency**: charts are hand-written SVG. Do not touch `package.json` / lockfile.

## 1. Lanes and file ownership

| Lane | Owns (create/edit only these) |
|---|---|
| **A: tokens + primitives** | `web/scripts/build-tokens.mjs`, `web/src/design/**` (except `tokens.json`, read-only), `web/src/ui/**`, `web/docs/signal-dark/decisions/A-tokens-primitives.md` |
| **B: shell + navigation** | `web/src/shell/**`, `web/docs/signal-dark/decisions/B-shell.md` |
| **C: data + widgets** | `web/src/widgets/**`, `web/src/demo/**`, `web/docs/signal-dark/decisions/C-widgets.md` |
| **Integrator (main agent)** | `web/src/App.tsx`, `web/src/main.tsx`, `web/src/index.css`, `web/index.html`, `web/package.json`, this file, `web/docs/signal-dark/IMPLEMENTATION_NOTES.md` |

Need a change outside your paths? Don't make it: write it under "Requests to integrator" in your
decisions file.

## 2. Tokens → CSS custom properties

`web/scripts/build-tokens.mjs` (Node, no deps) reads `src/design/tokens.json` and writes
`src/design/tokens.css` (committed, regenerated with `node scripts/build-tokens.mjs`).

Naming rule: drop the `primitive.` / `semantic.` root, join the rest with `-`, prefix `--sd-`.
Aliases stay aliases (`var(--sd-…)`). Dimensions become `px`, colors their `hex`, font families
a CSS font stack.

| Token path | CSS variable |
|---|---|
| `semantic.color.surface.canvas` / `.sidebar` / `.card` / `.elevated` | `--sd-color-surface-canvas` / `-sidebar` / `-card` / `-elevated` |
| `semantic.color.text.primary` / `.secondary` / `.muted` / `.on-accent` | `--sd-color-text-primary` / `-secondary` / `-muted` / `-on-accent` |
| `semantic.color.border.subtle` | `--sd-color-border-subtle` |
| `semantic.color.action.primary` / `.secondary` / `.focus` | `--sd-color-action-primary` / `-secondary` / `-focus` |
| `semantic.color.state.success` / `.warning` / `.danger` / `.info` | `--sd-color-state-success` / `-warning` / `-danger` / `-info` |
| `semantic.space.card-padding` / `.page-gap` / `.section-gap` | `--sd-space-card-padding` (20px) / `--sd-space-page-gap` (24px) / `--sd-space-section-gap` (32px) |
| `semantic.radius.card` / `.control` | `--sd-radius-card` (12px) / `--sd-radius-control` (8px) |
| `primitive.space.1…7` | `--sd-space-1` … `--sd-space-7` (4, 8, 12, 16, 24, 32, 40px) |
| `primitive.font.size.caption` / `body-sm` / `body` / `section` / `page` | `--sd-font-size-caption` (12) / `-body-sm` (14) / `-body` (16) / `-section` (20) / `-page` (28) |
| `primitive.font.weight.regular` / `medium` / `semibold` | `--sd-font-weight-regular` / `-medium` / `-semibold` |
| `primitive.font.family.ui` / `metric` | `--sd-font-family-ui` / `-metric` |
| `primitive.color.*`, `primitive.radius.*` | `--sd-color-<group>-<name>`, `--sd-radius-sm/md/lg` (primitives: **components use semantic variables only**) |

**Local tokens** (values not in the DTCG file, e.g. focus ring width, hover tint, transition
duration, second chart series, overlay scrim, control height) live in `src/design/local.css` as
`--sd-local-*`, each with a comment marking it as an implementation decision and why. Lane A
defines them. Lanes B/C may only consume them; if they need a new one, they request it (§1) and
meanwhile derive it locally from semantic tokens with `color-mix()`, never a raw hex.

Lane A defines at least: `--sd-local-focus-ring` (full `outline` shorthand),
`--sd-local-focus-offset`, `--sd-local-control-height` (≥ 40px), `--sd-local-hit-min` (44px),
`--sd-local-duration` (+ set to `0ms` under `prefers-reduced-motion: reduce`),
`--sd-local-hover-surface`, `--sd-local-accent-subtle` (selected background),
`--sd-local-series-2`, `--sd-local-series-3` (neutral/secondary chart series, distinguishable
from cyan), `--sd-local-scrim`, `--sd-local-shadow-overlay` (drawer/popover only).

**Rule: no raw hex/rgb, px radius or ad-hoc spacing in component CSS.** Allowed literals:
`0`, `1px` borders, `100%`, layout fractions, breakpoints (§4), `em` for icon sizing.

## 3. Shared component API (frozen; additive optional props only)

Lane A owns these. Stubs with the final signatures are already in `src/ui/`; lane A replaces the
bodies. Import from `src/ui` (barrel `index.ts`).

```ts
// Button.tsx
type ButtonVariant = 'primary' | 'secondary' | 'ghost'
interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant          // default 'secondary'
  size?: 'sm' | 'md'               // default 'md'
  icon?: ReactNode                 // leading icon (decorative, aria-hidden)
  iconOnly?: boolean               // hides label visually; requires aria-label
  loading?: boolean                // aria-busy, disabled interaction, spinner + label kept for AT
  pressed?: boolean                // toggle button → aria-pressed
}
// Input.tsx
interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label: string; hideLabel?: boolean; hint?: string; error?: string; icon?: ReactNode
}
// Select.tsx (native <select>)
interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'size'> {
  label: string; hideLabel?: boolean; hint?: string; error?: string
  options: { value: string; label: string; disabled?: boolean }[]
}
// StatusBadge.tsx: never color-only; each tone has its own icon shape + text label
type StatusTone = 'success' | 'warning' | 'danger' | 'info' | 'neutral'
interface StatusBadgeProps { tone: StatusTone; label: string; count?: number; className?: string }
// FeedbackState.tsx
interface EmptyStateProps   { title: string; description?: string; action?: ReactNode; compact?: boolean }
interface LoadingStateProps { label: string; lines?: number; compact?: boolean }   // role="status"
interface ErrorStateProps   { title: string; description?: string; onRetry?: () => void; compact?: boolean } // role="alert"
// VisuallyHidden.tsx
function VisuallyHidden(props: { children: ReactNode }): JSX.Element
// format.ts: it-IT locale helpers, tabular numbers are a CSS concern
formatNumber(n, opts?), formatPercent(fraction, digits?), formatDuration(ms), formatDelta(fraction) // "+4,2%" / "−1,3%"
```

Lane B owns the shell API (consumed by the integrator in `App.tsx`):

```ts
// src/shell/AppShell.tsx: skip link → #main, persistent sidebar on wide, modal drawer on narrow
interface AppShellProps {
  brand: ReactNode            // product name/logo slot (demo name, no third-party marks)
  sidebar: ReactNode          // usually <SidebarNav/>
  sidebarFooter?: ReactNode
  topbar?: ReactNode          // global actions (right side of the top bar)
  children: ReactNode         // page content, rendered inside <main id="main" tabIndex={-1}>
}
// src/shell/SidebarNav.tsx
interface NavItem  { id: string; label: string; icon: LucideIcon; badge?: string; disabled?: boolean }
interface NavGroup { id: string; label?: string; items: NavItem[] }
interface SidebarNavProps { label: string; groups: NavGroup[]; currentId: string; onNavigate: (id: string) => void }
// src/shell/PageHeader.tsx
interface PageHeaderProps { title: string; subtitle?: string; meta?: ReactNode; actions?: ReactNode; children?: ReactNode /* filter row */ }
```

Navigating closes the drawer (AppShell exposes this via context: `useShell().closeDrawer()`).

Lane C owns `src/widgets/**` (FilterBar, KpiCard, ChartCard + SVG charts, DataTable, MiniBar)
and `src/demo/**` (demo data, scenario switch, `DashboardPage`). The integrator only imports
`DashboardPage` from `src/demo/DashboardPage.tsx`:

```ts
interface DashboardPageProps { scenario: DemoScenario }   // 'data' | 'loading' | 'empty' | 'error'
export type DemoScenario = …  // from src/demo/scenario.ts, with DEMO_SCENARIOS: {value,label}[]
```

## 4. Layout and breakpoints (implementation decisions, not from the references)

No breakpoint is visible in the sources. Starting points, to be validated by testing the actual
composition and adjusted (record the final values in your decisions file):

- **Shell:** sidebar persistent at `min-width: 1024px`, modal drawer below. Sidebar width is a
  local token (`--sd-local-sidebar-width`, lane B defines it in `src/shell/shell.css`, ≈ 248px).
- **Dashboard grid:** 12 fluid columns with `--sd-space-page-gap` gutters at ≥ 1280px; 6 columns
  from 720px; 1 column below. Card spans 3/4/6/8/12 on 12 columns.
- Test viewports: 1440×900, 1280×800, 1024×768, 768×1024, 390×844. Nothing may overflow the
  viewport horizontally except an intentionally scrollable table wrapper.

## 5. Shared rules

- Italian UI copy, short labels, explicit period and unit on every number; `it-IT` formatting;
  `font-variant-numeric: tabular-nums` on KPIs and table numbers.
- One cyan accent: active nav item, selection, primary series, primary CTA. State colors only
  with icon/text. Multiple chart series differ by more than color (dash pattern, marker shape or
  direct labels) and always have a legend.
- Semantic HTML; every interactive element has `default/hover/focus-visible/disabled` (+
  `pressed/loading/error/empty` where relevant). Focus ring = `--sd-local-focus-ring`. Hit area
  ≥ 44×44 where space allows. Respect `prefers-reduced-motion`.
- These states and every unlisted value are **our product decisions, not facts of the original
  designs**: say so in code comments only where non-obvious, and in your decisions file.
- Demo data is labelled "Dati demo" in the UI; no third-party logos, copy or imagery.
- Comment density: sparse, explain *why*. Code and comments in English; UI copy in Italian.
- Before reporting done: `cd web && npm run lint && npm run typecheck` must pass for your files.
