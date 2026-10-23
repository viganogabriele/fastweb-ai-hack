# Maison: visual system (WEB-10)

Maison replaces Signal Dark as the look of the web UI. It borrows the language of fashion-house
sites and lookbooks (Valentino-like) without copying any brand asset: ivory paper, ink type,
hairline rules and **one signature red** used only where something needs attention.

## What changed and what did not

- **Same token names.** `src/design/tokens.json` keeps the semantic paths (`color.surface.card`,
  `color.text.primary`, `color.action.primary`, …), so every `--sd-*` variable and every `sd-*`
  class still exists. Pages written for Signal Dark pick up Maison without edits. Regenerate the
  CSS with `node scripts/build-tokens.mjs`, check contrast with `node scripts/check-contrast.mjs`
  (all pairs pass WCAG AA).
- **New tokens:** `--sd-color-accent-signature` (the red), `--sd-font-family-display` (serif).
  Local tokens in `local.css`: `--sd-local-tracking-label`, `--sd-local-tracking-button`,
  `--sd-local-font-size-micro`.
- **Fonts are self-hosted** (`@fontsource-variable/bodoni-moda`, `@fontsource-variable/jost`, OFL),
  so the demo works offline.

## Rules

| Element | Rule |
|---|---|
| Page and section titles | Bodoni Moda, regular weight, slight negative tracking |
| Big figures (KPI) | Bodoni Moda, lining numerals. Small numbers stay in Jost: Didone digits break down below ~20px |
| Ids, SKUs, tables | Jost, tabular numerals, light positive tracking. Never the serif |
| Microlabels (field labels, table heads, nav groups, KPI labels) | 11px uppercase, `0.14em` tracking |
| Buttons | Uppercase tracked. Primary = ink fill, secondary = ink outline that fills on hover |
| Status tags | Square, uppercase. Only `danger` is filled (red); the others are outlined |
| Signature red | Brand rule, current page marker, focus ring, critical priority, overdue/≤24h deadlines. Nothing decorative |
| Surfaces | Ivory page, white cards, 2px radius, no shadows except overlays. Lists are ruled rows, not stacked boxes |

## Overview

`src/sections/Overview.tsx` renders the Panoramica as an evening report: a KPI band, "Da decidere"
(open cases due within 48h of the run cutoff, never of wall-clock time), priority and office
breakdowns, a stores table that filters the case list, and the case list itself.

## Developing without a backend

`npm run dev:mock` serves `/api/*` from `mock-api/` (schema-typed synthetic data, store ids and
SKUs from `generated/sources/erp/master_data/`, style names as renamed by DATA-04). `npm run dev`
(or `make dev`) talks to the real backend; the UI code is identical in both modes.
