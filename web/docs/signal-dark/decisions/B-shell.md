# Lane B: shell and navigation

All choices below are **our implementation decisions**, not measurements or observed interactions from the reference designs.

- **Breakpoint — implementation decision:** persistent sidebar at `min-width: 1024px`; modal drawer below. CSS and the `matchMedia` subscription deliberately share this threshold. Content padding increases from `space.4` to `space.page-gap` at 768px.
- **Sidebar width — implementation decision:** `--sd-local-sidebar-width` is 248px, derived as `space.7 × 5 + space.6 + space.4`. The narrow drawer is capped at viewport width minus `space.6` to leave a reachable scrim.
- **Scroll — implementation decision:** the shell occupies `100dvh`; main scrolls independently, the sidebar remains anchored, and its navigation scrolls independently when necessary. Sidebar header/footer stay in place.
- **Drawer — implementation decision:** one navigation instance serves both layouts. On narrow screens the closed sidebar is hidden and inert. Opening adds `role="dialog"`, `aria-modal`, a brand-derived accessible name, and moves focus to the close button. Main/topbar become inert and aria-hidden; the skip link is inert; body scrolling is locked with the previous inline overflow restored on cleanup. Tab/Shift+Tab cycle through enabled visible controls, including optional footer controls. Escape, scrim, close button and successful navigation close the drawer and restore focus to the menu trigger. Resizing an open drawer to desktop closes it, clears the lock and focuses main because the trigger disappears; resizing back does not reopen it.
- **Transition — implementation decision:** transform uses only `--sd-local-duration`; reduced motion supplied by lane A makes it zero. Visibility becomes immediate on open so focus can enter before animation. Closing can finish its slide while the sidebar is already inert. Only the drawer uses the shared overlay shadow.
- **Local tokens — implementation decision:** besides `--sd-local-sidebar-width`, shell CSS defines `--sd-local-shell-layer-scrim: 2`, `--sd-local-shell-layer-drawer: 3`, and `--sd-local-shell-layer-skip: 4`, scoped within an isolated shell stacking context. No new local colors are required. All surfaces, spacing, radii, typography, focus and state treatments consume the agreed tokens. It also consumes lane A's `--sd-local-line-height`.
- **Navigation — implementation decision:** active item uses cyan text, subtle cyan background, semibold type and a left indicator. Exactly the first matching ID receives `aria-current="page"`; callers must pass a current ID present in their groups. Disabled items use native disabled behavior and a dashed outline. Buttons have a minimum 44px height. Navigation invokes the callback before closing the narrow drawer.
- **Header — implementation decision:** the title retains page typography; actions, metadata and filters wrap. The intro uses a preferred basis derived from the spacing scale. Long title/brand text can wrap instead of forcing horizontal page overflow.

## Verification

- `npm run lint` and `npm run typecheck` pass. Shell files have no lint warnings; any concurrent lane warnings are outside this lane's ownership.
- Chromium headless via the existing Playwright installation rendered the standalone playground at 1440×900, 1280×800, 1024×768, 768×1024 and 390×844. At every width, document scroll width equalled viewport width and main scroll width equalled its client width; exactly one item had `aria-current`. Sidebar measured 248px, persistent at 1024+ and hidden until opened below.
- Keyboard assertions passed: first Tab reaches the skip link; Enter focuses `#main`; opening focuses the close button; reverse Tab wraps to the last enabled item and forward Tab wraps back; Escape restores menu focus. Navigation updates current item and closes the drawer. Scrim closes it. Resizing an open drawer to desktop clears modal/body-lock state and focuses main; returning narrow keeps it closed. Reduced motion yields zero transition duration. No page runtime errors.
- Inspected desktop and mobile screenshots (`/tmp/signal-dark-b-desktop.png`, `/tmp/signal-dark-b-mobile.png`). The mobile capture waits for the transition to finish.
- T3 preview snapshot failed twice with `Preview automation snapshot timed out after 15000ms.` Browser verification therefore used standalone headless Chromium, as permitted by the preview fallback rule.
- Ran `npx -y @memi-design/cli@2.7.9 diagnose web/src --json --no-write --fail-on none` before the implementation and again after changes. The scoped source-tree score reported 61 during implementation and 61 on the final run; the checker is not a substitute for runtime testing and includes other lanes and the old app entry point. No isolated before/after shell score is claimed because the shared source tree changed concurrently.

## Requests to integrator

- Import `src/design/index.css` once from the app entry point (or the equivalent `base.css`, which imports tokens/local). Remove Vite starter root/body sizing and light-mode styles so the shell can fill the viewport. The shell itself imports its co-located CSS.
- Render one `AppShell`; it owns the only `<main id="main">`. Do not wrap it or page children in another main landmark. `SidebarNav` provides the named nav landmark; pass an accessible brand (text or a logo with an accessible name).
- Keep `SidebarNav` inside `AppShell` so `useShell()` has its provider. Supply unique group/item IDs and a valid `currentId`; render the page corresponding to the selected ID. Disabled items cannot navigate.
- Render `PageHeader` in the page content. Lane C's `DashboardPage` may already supply it: check before adding a second title. The example below shows shell-only composition.
- Update the shared `STATUS.md` WEB-01 task when integrating; it is outside lane B's allowed paths.
- The optional playground remains at `/preview/b.html` and is not imported by the product bundle. Its dedicated port 5174 dev server was stopped after validation.

## Exact App.tsx usage

```tsx
import { useState } from 'react'
import { Activity, Layers } from 'lucide-react'
import { AppShell, PageHeader, SidebarNav } from './shell'
import { Button, StatusBadge } from './ui'

export default function App() {
  const [currentId, setCurrentId] = useState('overview')

  return (
    <AppShell
      brand="Signal Dark"
      sidebar={
        <SidebarNav
          label="Navigazione principale"
          currentId={currentId}
          onNavigate={setCurrentId}
          groups={[{
            id: 'monitor',
            label: 'Monitoraggio',
            items: [
              { id: 'overview', label: 'Panoramica', icon: Activity },
              { id: 'sources', label: 'Sorgenti', icon: Layers, badge: '12' },
            ],
          }]}
        />
      }
      sidebarFooter={<span>Ambiente dimostrativo</span>}
      topbar={<Button>Area demo</Button>}
    >
      <PageHeader
        title={currentId === 'overview' ? 'Panoramica' : 'Sorgenti'}
        subtitle="Attività degli ultimi 7 giorni"
        meta={<StatusBadge tone="neutral" label="Dati demo" />}
        actions={<Button variant="primary">Esporta</Button>}
      >
        {/* Put labelled filter controls here. */}
      </PageHeader>
      {currentId === 'overview'
        ? <section aria-label="Panoramica">Contenuto della panoramica</section>
        : <section aria-label="Sorgenti">Contenuto delle sorgenti</section>}
    </AppShell>
  )
}
```
