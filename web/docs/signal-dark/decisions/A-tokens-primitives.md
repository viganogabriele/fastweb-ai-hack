# Lane A: tokens and primitives

All choices below are local implementation decisions for this demo, **not facts of the reference designs**. `tokens.json` is unchanged. The generated CSS preserves aliases and exports 55 variables using CONTRACT §2 names. Unknown aliases, circular aliases, unsupported types and name collisions throw before writing output.

## CSS entry and API

Import `src/design/index.css` once before application styles. It imports `base.css`, `tokens.css` and `local.css`. Import components/helpers from `src/ui`; every frozen export and signature remains compatible. Component CSS is imported by its TSX module.

## Local tokens

| Token | Value | Implementation reason |
| --- | --- | --- |
| `--sd-local-focus-ring` | `2px solid var(--sd-color-action-focus)` | a 2px cyan outline stays distinct on every dark surface. |
| `--sd-local-focus-offset` | `3px` | separate the focus outline from the control border. |
| `--sd-local-control-height` | `44px` | 44px controls support touch and compact desktop layouts. |
| `--sd-local-hit-min` | `44px` | reserve a minimum 44px square interactive target. |
| `--sd-local-duration` | `160ms` | short transitions acknowledge actions without delaying them. |
| `--sd-local-spin-duration` | `900ms` | a slower spinner remains legible while loading. |
| `--sd-local-ease` | `ease-out` | restrained easing keeps interactions predictable. |
| `--sd-local-hover-surface` | `color-mix(in srgb, var(--sd-color-surface-elevated) 90%, var(--sd-color-text-primary))` | lighten the raised surface for hover without a new accent. |
| `--sd-local-accent-subtle` | `color-mix(in srgb, var(--sd-color-action-primary) 12%, var(--sd-color-surface-card))` | a muted cyan surface communicates selection. |
| `--sd-local-accent-hover` | `color-mix(in srgb, var(--sd-color-action-primary) 85%, var(--sd-color-text-primary))` | brighten primary hover while retaining dark text contrast. |
| `--sd-local-accent-pressed` | `color-mix(in srgb, var(--sd-color-action-primary) 85%, var(--sd-color-surface-card))` | darker cyan provides tactile pressed feedback. |
| `--sd-local-series-2` | `var(--sd-color-text-secondary)` | a neutral gray series avoids implying a state. |
| `--sd-local-series-3` | `color-mix(in srgb, var(--sd-color-state-info) 80%, var(--sd-color-text-secondary))` | mix neutral text and the info hue for a distinct blue comparison series. |
| `--sd-local-scrim` | `color-mix(in srgb, var(--sd-color-surface-sidebar) 72%, transparent)` | translucent sidebar black dims content behind a modal. |
| `--sd-local-shadow-overlay` | `0 16px 48px color-mix(in srgb, var(--sd-color-surface-sidebar) 65%, transparent)` | shadow is reserved for overlays, never flat cards. |
| `--sd-local-control-border` | `color-mix(in srgb, var(--sd-color-text-muted) 75%, var(--sd-color-surface-card))` | visible control edges exceed decorative card-border contrast. |
| `--sd-local-disabled-surface` | `var(--sd-color-surface-canvas)` | disabled controls retain readable text and a distinct cursor. |
| `--sd-local-radius-pill` | `999px` | pill rounding is limited to status labels and spinners. |
| `--sd-local-line-height` | `1.5` | line height balances dense UI and multiline Italian labels. |
| `--sd-local-hidden-size` | `1px` | single-pixel clipping keeps hidden labels available to AT. |
| `--sd-local-spinner-stroke` | `2px` | a 2px spinner stroke matches the focus indicator. |
| `--sd-local-skeleton-height` | `var(--sd-font-size-body-sm)` | skeleton lines use body-sized height and staggered widths. |
| `--sd-local-skeleton-short` | `65%` | alternate line widths suggest content without fake data. |
| `--sd-local-skeleton-last` | `45%` | a short final line prevents a solid placeholder block. |

Under `prefers-reduced-motion: reduce`, both duration variables become `0ms`; global transitions, animation and smooth scrolling are disabled. Button and field styles also carry explicit local guards.

## Behavior and remaining local choices

- Buttons default to `type="button"`, secondary, medium. Both sizes retain a 44px minimum target; small uses 12px horizontal padding, medium 16px. Icon-only uses 8px padding. Icons are decorative and 1.15em; feedback icons use 2em. Spinner rotates linearly by one turn and remains a static visible arc with reduced motion. Loading disables interaction, sets `aria-busy`, and retains children/explicit accessible labels. Development builds warn if icon-only lacks an explicit `aria-label`. `pressed` controls `aria-pressed`; active/pressed change the surface and border without moving layout.
- Native input/select behavior and browser focus remain intact. IDs use React `useId` unless supplied; label is persistent or visually clipped. Hint, error and caller-provided description IDs are combined. An error forces `aria-invalid=true` and adds a distinct CircleAlert icon with the error text. Labels use secondary text; hints and placeholders use muted text. Controls use an enhanced local border because the semantic card border is decorative. Disabled text remains readable rather than faded by opacity.
- Status shapes are CircleCheck (success), TriangleAlert (warning), CircleX (danger), Info (info), Minus (neutral). All include literal text and optional localized counts, with a separator before the count. Card backgrounds keep state text contrast predictable. No status is encoded only with color.
- Empty feedback uses Inbox; error feedback uses CircleAlert and a secondary retry Button with RotateCcw. Feedback titles use paragraphs to avoid imposing heading levels on consumers. Compact feedback uses 16px padding/8px gap; standard uses 40px vertical padding/12px gap. Loading is a polite `role="status"` with a clipped label and static, decorative skeletons; default three lines, finite inputs clamped to 1–12 lines. Skeletons do not imply progress and do not animate.
- Base styles use dark `color-scheme`, a lightweight border-box/margin reset, token typography and 1.5 line height. Selection uses on-accent text on cyan; scrollbars use muted text on canvas. Visually hidden content uses single-pixel clipping and `inset(50%)`, avoiding horizontal overflow. `.sd-num` supplies metric font/tabular numbers.
- Format helpers use `it-IT`: percent precision defaults to one digit, durations below 1000ms round to whole ms and otherwise show seconds with at most one digit. Deltas use `+`, Unicode minus `−` (U+2212), and `±` for zero. Numeric formatting does not change the values passed by callers.
- `preview/a.html` and `src/ui/Playground.tsx` are an isolated, optional state showcase; they are not imported by the application barrel. Its field grid changes from three columns to one at 720px, solely for reviewing the primitives. Playground controls use Italian demo copy.

## Contrast verification

Command: `node scripts/check-contrast.mjs` from `web/`. Zero dependencies; reads the DTCG source, recursively resolves aliases, reads local color declarations and evaluates sRGB `color-mix()` values. Focus colors are read from the actual outline shorthand. Each listed pair passes. Normal text is checked against 4.5:1; passing that also exceeds the 3:1 large-text requirement. Focus, control edges and comparison series are checked as non-text UI at 3:1. These are opaque foreground/background checks, not an assertion of full dashboard WCAG compliance.

No source palette correction was necessary. Enhanced control borders are a local accessibility addition; semantic decorative card borders are not treated as control indicators. Neutral status uses secondary text on card (included below). Disabled controls use muted text on canvas; secondary-button default uses primary on elevated (both included below).

| Foreground | Background | Ratio | Minimum | Result |
| --- | --- | ---: | ---: | --- |
| color-text-primary | color-surface-canvas | 17.89:1 | 4.5:1 | PASS |
| color-text-secondary | color-surface-canvas | 10.72:1 | 4.5:1 | PASS |
| color-text-muted | color-surface-canvas | 7.97:1 | 4.5:1 | PASS |
| color-text-primary | color-surface-sidebar | 18.98:1 | 4.5:1 | PASS |
| color-text-secondary | color-surface-sidebar | 11.37:1 | 4.5:1 | PASS |
| color-text-muted | color-surface-sidebar | 8.45:1 | 4.5:1 | PASS |
| color-text-primary | color-surface-card | 16.48:1 | 4.5:1 | PASS |
| color-text-secondary | color-surface-card | 9.87:1 | 4.5:1 | PASS |
| color-text-muted | color-surface-card | 7.34:1 | 4.5:1 | PASS |
| color-text-primary | color-surface-elevated | 14.75:1 | 4.5:1 | PASS |
| color-text-secondary | color-surface-elevated | 8.84:1 | 4.5:1 | PASS |
| color-text-muted | color-surface-elevated | 6.57:1 | 4.5:1 | PASS |
| color-text-on-accent | color-action-primary | 12.75:1 | 4.5:1 | PASS |
| color-state-success | color-surface-card | 12.27:1 | 4.5:1 | PASS |
| color-state-warning | color-surface-card | 9.68:1 | 4.5:1 | PASS |
| color-state-danger | color-surface-card | 8.20:1 | 4.5:1 | PASS |
| color-state-info | color-surface-card | 8.83:1 | 4.5:1 | PASS |
| color-action-primary | color-surface-card | 11.06:1 | 4.5:1 | PASS |
| color-action-focus | color-surface-card | 11.06:1 | 3:1 | PASS |
| color-action-focus | color-surface-canvas | 12.01:1 | 3:1 | PASS |
| color-text-primary | local-hover-surface | 11.06:1 | 4.5:1 | PASS |
| color-text-secondary | local-hover-surface | 6.63:1 | 4.5:1 | PASS |
| color-text-muted | local-hover-surface | 4.93:1 | 4.5:1 | PASS |
| color-text-primary | local-accent-subtle | 12.86:1 | 4.5:1 | PASS |
| color-text-secondary | local-accent-subtle | 7.70:1 | 4.5:1 | PASS |
| color-text-muted | local-accent-subtle | 5.73:1 | 4.5:1 | PASS |
| color-text-on-accent | local-accent-hover | 13.29:1 | 4.5:1 | PASS |
| color-text-on-accent | local-accent-pressed | 9.51:1 | 4.5:1 | PASS |
| local-control-border | color-surface-card | 4.66:1 | 3:1 | PASS |
| local-control-border | color-action-secondary | 4.17:1 | 3:1 | PASS |
| local-series-2 | color-surface-card | 9.87:1 | 3:1 | PASS |
| local-series-3 | color-surface-card | 9.00:1 | 3:1 | PASS |

## Validation

- `node scripts/build-tokens.mjs`: generated 55 variables; unknown/circular alias rejection separately exercised with in-memory fixtures.
- `node scripts/check-contrast.mjs`: 32/32 pairs pass; lowest checked text ratio 4.93:1 and lowest UI ratio 4.17:1.
- `npm run lint` and `npm run typecheck`: pass with no warnings in the final run.
- Browser playground: checked all five viewport requests (1440×900, 1280×800, 1024×768, 768×1024, 390×844; the user's browser reports ~1px viewport rounding), no horizontal overflow. Native select change, retry callback, keyboard Space toggle and Tab focus verified. Loading accessible names and disabled interaction confirmed. Every description ID resolves to a rendered hint/error. Inspected loaded reduced-motion media rules; OS motion preference was not changed.
- T3 snapshots failed twice with `Preview automation snapshot timed out after 15000ms.`; Brave via the computer-use connector supplied screenshots and DOM evidence instead.
- Memi diagnose (2.7.9) before/after score: 60/60, broad repository scope including unrelated static documents. Its remaining local-duration warning is a naming false positive: the tool expects `--motion-*`, while this contract requires `--sd-local-*`. It is not a browser or complete accessibility audit. React checklist reviewed: stable keys, native semantics, no render-time state mutation, type-only imports and explicit accessible names.

## Requests to integrator

- Import `./design/index.css` once in `main.tsx` before application styles. Remove scaffold `index.css` body/root/control rules that compete with this reset. Lane A did not edit these files.
- Keep the generated `tokens.css` in the final change. Optionally add `node scripts/build-tokens.mjs` and `node scripts/check-contrast.mjs` to package/CI scripts; package files remain integrator-owned.
- Lanes B/C should consume the local focus, target, hover and series variables rather than inventing parallel values. Series 2/3 still need dash patterns, markers or direct labels in chart code.
- Update the shared STATUS task line in the final integration change; this file is outside lane A ownership.
- Final integrated shell/widget responsive review remains the integrator's responsibility. Lane A implementation has no unfinished deliverables.
