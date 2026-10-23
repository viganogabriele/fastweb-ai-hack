# pitch

Team reading pack for the pitch. Dark-mode, landscape A4 PDFs, about the idea and the process
rather than the stack. Read them in order.

| PDF | What | Read time |
|---|---|---|
| `01-the-idea.pdf` | The problem, the idea, the rule ("AI reads, code counts, humans decide"), one story end to end, what it is and isn't, glossary | 10 min |
| `02-the-process.pdf` | The seven stations from store note to decision, how to talk about each, and the five pieces to highlight | 12 min |
| `03-pitch-playbook.pdf` | The jury and its criteria, three messages, where the money leaks, 4-minute run sheet, numbers we can say, words to use and avoid, buyer and pilot | 10 min |
| `04-tackling-bleeds.pdf` | Hard questions with short answers, plus our own loose ends to close before the demo | 12 min |

Numbers come from the dev-store evaluations in PR #162 (EVL-02) and PR #163 (EVL-04). No
hold-out result exists yet: update pack 3 and pack 4 once EVL-05 (#128) lands.

## Edit and rebuild

Sources are plain HTML in `src/` sharing `src/style.css` (palette from `web/src/design/tokens.css`,
fonts Inter and Bodoni Moda under the OFL). Each `<section class="page">` is one fixed page.

```sh
python3 pitch/build.py                 # all documents
python3 pitch/build.py 04-tackling-bleeds
```

It needs Chrome or Chromium (found on `PATH`, in the Playwright cache, or via `CHROME=...`). The
build fails if a page's content overflows; open the HTML in a browser to see the page outlined
in red.
