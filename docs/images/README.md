# README screenshots

These PNGs are actual application captures, not mockups. They illustrate the
recorded synthetic development demo at `2026-10-22T20:00:00Z` using application
code from `4498c6d` (the starting point of DOC-02). They do not document a live
customer deployment or a hold-out evaluation.

## Reproduce the views

From the repository root, run `make setup` and `make demo`, then open
`http://localhost:5173`. Use the light theme, a 1440 × 1000 CSS-pixel viewport,
Italian locale and UTC timezone. Use a 1440 × 1100 viewport for the market view
to include the chart axis and legend. The committed captures use reduced motion so
charts and counters are settled. Wait for fonts, API responses and visible
product photographs to finish loading before capturing the viewport.

| Image | View |
| --- | --- |
| `overview.png` | `#/panoramica`, default operational view; decision list collapsed. |
| `market.png` | `#/panoramica`, select the **Mercato** tab. |
| `products.png` | `#/prodotti`, default catalog without search or filters. |
| `case-detail.png` | `#/casi/case-lon01-j20931a00012-999-2-20261021/v1`, the recorded London order case. |
| `sources.png` | `#/fonti`, expand `doc-20260918-2115-mil01` to show its linked evidence. |
| `pipeline.png` | `#/pipeline`, the selected run's module graph. |

Keep the selected run `production-demo-20261022`. Do not approve proposals or
submit recordings to stage a screenshot. Capture the application viewport
without browser chrome, private tabs, credentials, voice capability links or
QR codes. Recheck the README captions when replacing images.

The catalog's product photographs belong to Valentino and serve as illustrative
references for synthetic items; see [catalog attribution](../../data/catalog/README.md).
The screenshots do not grant rights to those photographs.
