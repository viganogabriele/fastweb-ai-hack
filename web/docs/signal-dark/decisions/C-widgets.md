# Lane C: dashboard widgets and demo data

All choices below are **our implementation decisions**, not measurements or behaviors established
by the reference designs. Ownership is limited to `src/demo/`, `src/widgets/`, and this file.

## Composition and breakpoints

**Implementation decision:** use the contract's viewport breakpoints, with conservative chart
stacking at intermediate widths. The dashboard renders content only and begins with FilterBar.

- Below 720px: one fluid column; four KPI cards stack. Filter controls wrap naturally and the
  search input grows to available width. Bar labels and values stack above their SVG bars.
- From 720px to 1279px: six columns; KPI cards span three columns each. Charts, methodology
  panel, and detail section span all six columns. This avoids squeezing chart labels when the
  shell sidebar becomes persistent at 1024px.
- From 1280px: twelve columns; KPIs span three each; time trend and service comparison span
  eight; distribution and methodology span four; detail spans twelve.
- Gutters use `--sd-space-page-gap`; panels use `--sd-space-card-padding`.

**Implementation decision and verification:** screenshots were captured in local headless Chromium
at 1440×900, 1280×800, 1024×768, 768×1024, and 390×844. The temporary playground reserved 248px
for the desktop sidebar at widths >=1024px; it did not render lane B's actual shell. At every width,
`document.documentElement.scrollWidth === innerWidth`. Only the labelled table region scrolls
horizontally when needed. Final whole-app composition remains the integrator's verification.

## Chart interaction and series

**Implementation decision:** the line plot has one keyboard focus stop, instructions in its
accessible name, and a persistent text tooltip linked with `aria-describedby`. Left/right arrows
move between points; Home/End select first/last points. Focus selects the first point; hover uses
vertical hit bands for each interval. Tooltip values include full date/time, current and comparison
request counts, and unit. A live status announces changes. The tooltip is in normal document flow,
so it does not cover data or require pointer precision. Blur clears the focused point unless hover
selects another point.

**Implementation decision:** the current period is cyan with a solid line and circular markers;
comparison is neutral (`--sd-local-series-2`) with a dashed line. Region segments use solid,
diagonal-stripe, and dot patterns; legends use solid, dashed, and dotted samples. The third segment
uses `--sd-local-series-3`. All charts have visible labels, legend, period, summary, and a native
"Mostra dati" disclosure containing a semantic table. Bar labels and exact values remain real text
outside the SVG bars; chart graphics are not bitmap images.

**Implementation decision:** ResizeObserver updates the line SVG viewBox to actual card width.
Five x-axis ticks are shown above 520px of plot-container width; three are shown at or below it.
All observations remain in the line and data table. Axis numbers use compact it-IT formatting;
tooltips and tables show exact counts. Y-axis has four ticks and a visible req unit. Bar and
regional labels are never truncated. No decorative animation is used; reduced-motion disables
any inherited dashboard animation/transition.

## Table and selection

**Implementation decision:** DataTable is generic over typed rows/columns, with a caption,
column scopes, button sorting, `aria-sort`, right-aligned tabular numeric cells, and a labelled,
focusable horizontal scroll region. The table keeps its headers and column structure on narrow
screens rather than transforming rows into disconnected cards. Its minimum width derives from
`--sd-font-size-body-sm`; only this region may overflow internally.

**Implementation decision:** each row and all visible rows can be selected. The select-all checkbox
reflects partial selection through its indeterminate property. Selection count and the demo bulk
action's acknowledgement are live statuses. "Segna esaminati · demo" clears selection and displays
an acknowledgement; it performs no network mutation. The dashboard remounts the table on filter,
period, or scenario changes to avoid retaining invisible selections. Sorting does not change the
underlying metrics. StatusBadge is supplied through a typed render column.

## Data and API boundary

**Implementation decision:** `data.ts` defines DashboardFilters, Metrics, ServiceRow, TimePoint,
CategoryPoint, DashboardData, and source service metadata. A fixed integer seed produces 60 days
of hourly observations for six fictional services across Europa, America, and Asia. No render-time
randomness or repository dataset is used. All time windows end at `DEMO_UPDATED_AT`,
2026-10-22T18:00:00Z (20:00 Europe/Rome). No system clock affects results.

**Implementation decision:** 24h/7d/30d windows compare against immediately preceding windows of
equal length. The 24h chart uses hourly bins; longer windows use daily bins. Request counts are
summed; errors are failed requests divided by total requests. Latency p95 is computed from merged
request-count histograms (60, 90, 120, 180, 240, 320, 480ms bins), not averages of service percentiles.
The p95 is interpolated linearly inside the bin that crosses 95% (bin values are upper bounds),
and each service has its own tail weight, so services and periods differ (integrator change).
Incident counts are illustrative end-of-window snapshots, with explicit previous snapshot counts.
The UI labels this distinction. Region/service/search filters apply before all aggregations.

**Implementation decision:** `scenario.ts` owns product states independently of the dataset.
`fetchDashboard(filters, scenario)` simulates 360ms latency and returns a discriminated
DashboardResponse union. The loading scenario deliberately remains a skeleton; error deliberately
remains an error after retry until the scenario changes. Empty filters also return the empty state.
Dashboard requests cancel stale completion updates on effect cleanup. All visible copy is Italian.

## Local tokens

**Implementation decision:** these local widget variables are scoped to `.sd-dashboard` in
`widgets.css`; no raw color is introduced:

- `--sd-local-widgets-tooltip`: `color-mix(in srgb, var(--sd-color-action-primary) 7%, var(--sd-color-surface-card))`.
- `--sd-local-widgets-stroke`: half of `--sd-space-1`, used for SVG strokes.
- `--sd-local-widgets-stroke-fine`: 0.375 of `--sd-space-1`, used for smaller SVG strokes.

Other colors, spacing, type, radius, focus, hit area, and secondary series consume the frozen
contract's variables. Literal SVG coordinates describe chart geometry and data, not design tokens.

## Verification

**Implementation decision:** verification targets behavior and coherent aggregates, rather than
mirroring rendering implementation in committed tests.

- `cd web && npm run lint && npm run typecheck`: passes, without lane C warnings.
- A temporary Node assertion script checked 252 combinations of period, region, service, and
  search: row/request/error/incident totals, timeline/current and previous totals, regional totals,
  service-bar totals, error ratios, and deterministic repeatability all pass.
- Default 30-day totals: 20,790,354 req; 56,883 failed req; p95 240ms; two open incidents.
  Previous comparison: 20,760,057 req; 56,772 failed req; p95 320ms; five open incidents.
- Local Playwright + system Chromium checked all requested viewport sizes, all four scenarios,
  all three periods, empty search, region filtering, reset, ascending/descending sorting, select
  all, bulk acknowledgement, data disclosure, keyboard tooltip navigation, focus, and reduced motion.
  No page JavaScript errors were observed.
- Screenshots were captured under `/tmp/signal-c-{1440,1280,1024,768,390}.png` and
  `/tmp/signal-c-{data,loading,empty,error}.png`; desktop/mobile captures were visually inspected.
  The temporary playground and its 5175 dev server were removed/stopped after verification.
- Computed token contrast against card surface: primary text 16.48:1; secondary text 9.87:1;
  success 12.27:1; danger 8.20:1; primary cyan 11.06:1. These are sampled dashboard pairs, not a
  complete assistive-technology audit or a guarantee about future token edits.
- The audit-frontend-design command
  `npx -y @memi-design/cli@2.7.9 diagnose web --json --no-write --fail-on none` was run before
  broad edits and again afterwards. Whole-web score moved 46 → 61 during the parallel build;
  scores include concurrent lanes and are not attributable solely to C. The remaining raw-color
  finding points to the pre-integration App/index and generated token CSS, outside C ownership.
- T3 preview snapshot timed out twice; headless local Chromium supplied the verification fallback.

## Requests to integrator

1. Import `DashboardPage` from `src/demo/DashboardPage.tsx` and mount
   `<DashboardPage scenario={scenario} />` inside AppShell after PageHeader. The page itself
   renders FilterBar, so do not duplicate that row in the header.
2. Import `DemoScenario` and `DEMO_SCENARIOS` from `src/demo/scenario.ts` for the header's scenario
   selector. The initial scenario should be `data`.
3. Optional PageHeader meta: `DASHBOARD_META` (plain Italian string) is re-exported by
   DashboardPage.tsx; `DEMO_UPDATED_AT` is also exported. The page independently shows "Dati demo".
4. Ensure the app imports lane A's `src/design/index.css` globally; widgets import their own CSS.
   No dependency, package, shell, or primitive edits are required from C.
5. Verify the actual shell and header composition at the same five widths, including keyboard
   drawer interaction. C tested reserved sidebar space, not the concurrently built shell.
6. Update WEB-01's task-board line as part of integration; C did not modify STATUS.md because the
   assignment restricts edits to lane C paths. No lane C implementation work remains unfinished.
