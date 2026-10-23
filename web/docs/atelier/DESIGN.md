# Atelier: visual system (WEB-10)

Atelier is the look of the web UI. It is a **dashboard first**: every reading task is set in
Inter with tabular figures, colour carries meaning (priority, state) and never decoration. The
fashion-house touch is restraint: warm neutrals instead of cold greys, one wine-red accent, a
serif wordmark, generous but consistent spacing.

**Light mode is the default and the presentation mode.** Dark mode is complete and opt-in through
the moon/sun button in the top bar; the choice persists in `localStorage` (`tessera-theme`). The OS
preference is ignored on purpose so a dark-mode laptop never switches the demo by itself.

## Tokens

- `src/design/tokens.json` keeps the semantic names (`color.surface.card`, `color.text.primary`,
  `color.action.primary`, …), so every `--sd-*` variable and `sd-*` class still exists and pages
  written earlier pick up the theme without edits.
- Each semantic colour declares its dark value in `$extensions["com.tessera.atelier"].modes.dark`.
  `node scripts/build-tokens.mjs` emits `:root` (light) and `:root[data-theme='dark']`.
- `node scripts/check-contrast.mjs` checks every pair in **both** modes; all pass WCAG AA.
- New tokens: `--sd-color-accent-signature` (wine red), `--sd-font-family-brand` (wordmark only).
  `local.css` adds `--sd-local-shadow-card` (none in dark mode) and dark overrides for scrim and
  overlay shadows.

## Rules

| Element | Rule |
|---|---|
| Text | Inter. 14px UI default, 12px minimum, 30px page titles, 17px card titles. Sentence case |
| Figures | Tabular numerals everywhere; KPIs 34px semibold |
| Colour | Wine accent = interaction (current page, focus, selection, links, primary brief). Red/amber/blue/grey = priority critical/high/medium/low. Volume bars are neutral |
| Status | Tinted chips with an icon, so meaning survives without colour |
| Surfaces | Warm page `#F5F4F1`, white cards, 12px radius, 1px border and a hairline shadow (light only) |
| Tables | Uppercase 12px heads on a raised band, 1px row rules, numbers right-aligned |
| Brand | Bodoni wordmark with a wine diamond. The serif is never used for reading text |

## Overview

`src/sections/Overview.tsx`: a one-sentence run brief with a button to the most urgent case, six
KPI cards, "Da decidere" (open cases due within 48h of the **run cutoff**, never wall-clock time),
priority and office breakdowns, a stores table that filters the case table, and the case table
(search, store, priority segments; each row opens the case).

## Developing without a backend

`npm run dev:mock` serves `/api/*` from `mock-api/` (schema-typed synthetic data; store ids and SKUs
from `generated/sources/erp/master_data/`, style names as renamed by DATA-04). `npm run dev` (or
`make dev`) talks to the real backend; the UI code is identical in both modes.
