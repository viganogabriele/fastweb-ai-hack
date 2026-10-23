# Tesseract hackathon pitch

Open **[index.html](index.html)** directly in a browser. It is the final, self-contained
deck: 12 slides, Italian, approximately five minutes, with embedded fonts and image.
No server, API, package installation or network connection is needed to present it.

The deck retains the `polinetwork-slides` presentation engine, with custom scenes
inspired by the user's TicketBuddy pitch reference: a perspective wall, flowing
signals, staged extraction and a visible human decision gate. Dark scenes alternate
with ivory and red while retaining Tesseract's typography and identity. Each slide
includes timed speaker notes. The source is [tesseract.slides.html](tesseract.slides.html).

## Controls

| Key | Action |
| --- | --- |
| Right / Left, Space, Page Down / Page Up | Navigate |
| Home / End | First / last slide |
| F | Fullscreen |
| O, then Escape | Overview / return to presentation |
| M | Pause / resume animation, preserving readable content |
| P or Ctrl+P | Presenter window with notes and timer |
| S | Print / save as PDF |

The navigation controls also appear at the bottom of the browser. Use Chrome,
Edge or Brave for PDF export, with no margins and background graphics enabled.
Open `index.html?static` for a motion-free version, or `index.html#5` to start at
a particular slide. The deck respects the system's reduced-motion preference.

Motion is specific to each scene: a scrolling 3D email wall (1), an interrupted
signal (2), a crossed-out assumption (3), packets travelling through the pipeline
to human review (4), source scanning and staged extraction (5), catalogue cards
assembling (6), an illustrative scenario drawing (7), a proposal and checks entering
in sequence (8), packets and sequential tool highlighting (9), a layered process
stack (10), proposed measures with scanning rules (11), and four tiles assembling
into the closing mark (12). The plot on slide 7 has no quantitative scale and is
not a measured forecast result. All scenes have static/reduced-motion variants.

Only the visible scene runs a JavaScript animation frame. Packet motion stops in
overview, static mode, reduced motion and when the page is hidden. CSS loops pause
when their scene is inactive, and M pauses all scenes at readable final states.

## Edit and rebuild

From the repository root, using Python 3 with its standard library:

```sh
python3 presentazione/scripts/build.py presentazione/tesseract.slides.html -o presentazione/index.html
python3 presentazione/scripts/check.py presentazione/index.html --shots /tmp/tesseract-presentation-shots
```

Edit the source rather than `index.html`. Scene styling is in `assets/brand.css`;
the wall and packet animation lifecycle are in `assets/scenes.js`.
The local build and check scripts are included so rebuilding does not require the
skill to be installed. The layout checker requires Chrome or Chromium; set
`CHROME=/absolute/path/to/chrome` if automatic detection fails. Screenshots go
outside the repository and are not part of the deliverable.

The motion regression checker requires Playwright and its browser binaries. It
accepts `--executable /path/to/browser` when testing an existing installation:

```sh
uv run --no-project --with playwright python presentazione/scripts/check_motion.py --browser firefox
uv run --no-project --with playwright python presentazione/scripts/check_motion.py --browser chromium
```

## Evidence and boundaries

The product narrative follows `docs/RFC-001-piattaforma.md`, `docs/findings.md`,
`docs/PLAN.md`, and the implemented case review UI and investigator contract.
The RFC takes precedence over older demo-script claims. The deck does not claim
measured ROI, forecast uplift, guaranteed lead time or production integrations.
Pilot metrics on slide 11 are proposed measurements, not completed results.

Slide 5 quotes the synthetic source email
`generated/sources/store_emails/MIL01/20261008_2215_MIL01.eml` exactly. Its two
afternoon requests are not a forecast. The illustrated decision on slide 8 is
not a calculated transfer for that case, and the approval button is part of an
illustration. In the prototype, approval creates a local draft.

Slide 6 uses an existing local Valentino photograph as a **category illustration**,
not as the actual synthetic cardigan or evidence of a real stockout. Attribution
and association limitations are retained in its visible caption and speaker notes;
see `data/catalog/README.md`. Original image source: [Valentino product reference](https://www.valentino.com/en-it/product-valentino-cotton-and-moulin%C3%A9-wool-jumper-with-panther-jacquard-VKC38DBMW_0AN).
The photograph is not used for historical pipeline evidence.

Inter and Bodoni Moda fonts are bundled with their SIL Open Font License notices
in `assets/fonts/`.

## Verification

The local build and Chromium layout check pass for all 12 slides, with no missing
assets or placeholders. All slides were inspected visually. PDF export was also
checked: 12 pages, approximately 1.5 MB, with dark/light/red scenes, diagram
connections and the highlighted email evidence retained.

A Chromium browser smoke check passed offline loading, moving 3D wall, pipeline
packet movement, scan animation, sequential tool highlighting, M pause/resume,
arrow navigation, Home/End, overview, actual presenter notes, 1366×768 fit and
mobile width. Changing the reduced-motion preference while the deck is open
freezes packet motion and removes movement. There were no remote requests or
runtime exceptions. JavaScript and Python syntax checks pass.

The motion regression also passes on Firefox and Chromium, both with native frame
timestamps and with an initial timestamp preceding scene registration. This timing
occurred naturally in Firefox and previously produced a negative packet index,
stopping the animation until pause/resume restarted it. Elapsed time is now clamped
at zero. The check covers automatic startup on a directly opened slide, keyboard
navigation, pause/resume, reduced motion and static mode without manual recovery.

The application-wide `make check` was not run: changes are confined to this standalone
presentation directory. Physical projector rendering and the five-minute spoken
delivery still need a human rehearsal.

## Suggested review handoff

Branch suggestion: `docs/tesseract-presentation`.

Conventional Commit suggestion: `docs(presentation): add scene-based Tesseract hackathon pitch`.

PR title suggestion: `Add scene-based Tesseract hackathon pitch`.

Ready-to-paste PR description:

> Add a 12-slide Italian sales pitch for the Tesseract hackathon prototype under
> `presentazione/`. The offline HTML uses Tesseract branding and custom visual scenes
> informed by the TicketBuddy reference, including a perspective email wall, flowing
> pipeline packets, source scanning and a human review gate. Keep synthetic examples
> and unmeasured benefits explicit. Include timed notes, editable source, local
> assets, pause/reduced-motion support and standalone build/layout-check scripts.
> Validation: Chromium layout and motion checks, offline navigation, presenter notes,
> pause/resume, reduced motion and 12-page PDF export. A Firefox/Chromium motion
> regression checks automatic startup, including the previous-frame timestamp that
> formerly caused a negative packet index and stopped the animation.

These are suggestions only; the work is left uncommitted for local review.
