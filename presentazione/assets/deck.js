/*
  PoliNetwork Slides: motore
  ←/→ Spazio PagSu/PagGiù · Home/Fine · F schermo intero · O panoramica · P (anche Ctrl+P) presentatore
  S stampa / PDF
  URL: ?static (niente animazioni) · ?check (controllo layout) · #N (vai alla slide N)
*/
(() => {
  const root = document.documentElement;
  const params = new URLSearchParams(location.search);
  const STATIC = params.has("static") || params.has("check") || params.has("embed");
  const CHECK = params.has("check");
  const EMBED = params.has("embed");
  const PRESENTER = params.has("presenter");
  const READ = root.classList.contains("read");
  if (STATIC) root.classList.add("static");
  if (EMBED) root.classList.add("embed");

  const LANG = (root.lang || "it").slice(0, 2);
  const T = {
    it: { image: "Immagine", prev: "Indietro", next: "Avanti", full: "Schermo intero", grid: "Panoramica", print: "Stampa / PDF", now: "Ora", next2: "Dopo", notes: "Note", end: "Fine", nonotes: "Nessuna nota." },
    en: { image: "Image", prev: "Previous", next: "Next", full: "Full screen", grid: "Overview", print: "Print / PDF", now: "Now", next2: "Next", notes: "Notes", end: "End", nonotes: "No notes." },
  }[LANG] || {};

  const stage = document.getElementById("stage");
  // sezioni: danno il nome in alto a destra, la slide a cui porta ogni voce dell'indice e il
  // sottotitolo della voce. Una sezione la apre un divisore .section (e la voce porta lì) oppure,
  // senza divisori, la sua prima slide con data-section="Titolo" (e data-sub="frase").
  // Indice, divisori e nome in alto sono scelte di chi scrive: ognuna funziona anche senza le altre.
  const sections = [];
  {
    const esc = (t) => t.replace(/&/g, "&amp;").replace(/</g, "&lt;");
    let title = "";
    stage.querySelectorAll(":scope > .slide").forEach((s) => {
      if (s.classList.contains("section")) {
        title = (s.querySelector(":scope > h1")?.textContent || "").trim();
        sections.push({ sub: s.querySelector(":scope > .sub")?.innerHTML || "", start: s });
        return;
      }
      if (s.dataset.section) {
        title = s.dataset.section;
        sections.push({ sub: esc(s.dataset.sub || ""), start: s });
      }
      if (sections.length && !sections.at(-1).start) sections.at(-1).start = s;
      if (title && !s.dataset.crumb) s.dataset.crumb = title;
    });
  }
  const slides = [...stage.querySelectorAll(":scope > .slide")];
  const total = slides.length;
  const icon = (name) => `<svg class="ico" aria-hidden="true"><use href="#i-${name}"/></svg>`;

  /* ---------- Presentatore: finestra separata ---------- */
  if (PRESENTER) return presenterView();

  /* ---------- Preparazione delle slide ---------- */
  const CENTERED = ["cover", "section", "thanks"];
  // L'orbit entra con la slide: un'animazione di opacità sul suo contenitore
  // isola il backdrop degli anelli, anche dopo l'ingresso con fill "both".
  const ANIM = [
    ".slide > h1", ".slide > .kicker", ".slide > .sub", ".body > .lead", ".body > .statement", ".body > p", ".body > ul:not([class])",
    ".body > .glass", ".body > .small", ".body > h2", ".body > table", ".body > .bars", ".body > .cloud > h2",
    ".agenda > li", ".irows > li > *", ".cards > *", ".stats > *", ".teams > *", ".timeline > li", ".compare > *",
    ".team > *", ".split > *", ".budget > .glass", ".fivex > *", ".vote > *", ".gallery > figure", ".screens > figure", ".people > .person",
    ".links > li", ".cover .meta > span", ".cover .brand", ".lockup", ".media > *", ".legend > li", "table.status tr",
    ".bars > .bar", ".body > .columns", ".cloud > span", ".thanks .qr", ".body > .summary", ".body > .next", ".body > dl", ".cols > *",
    "ol.points > li", "dl.terms > div", ".cover .intro", ".cover > .small", ".body > .quote", ".split > * > .quote", ".profile > *",
    ".panel > li", ".recap > ol > li", ".body > .device-stage", ".image-caption", ".metric > *",
  ].join(",");

  let sectionTitle = "";
  let partNo = 0;
  slides.forEach((s, idx) => {
    const centered = CENTERED.some((c) => s.classList.contains(c));
    if (s.classList.contains("section")) sectionTitle = (s.querySelector(":scope > h1")?.textContent || "").trim();
    // lettura: in alto a destra la sezione in cui si è
    const crumb = s.dataset.crumb === "off" ? "" : s.dataset.crumb || sectionTitle;
    if (!centered && crumb && root.dataset.crumb !== "off") s.insertAdjacentHTML("afterbegin", `<div class="crumb">${crumb.replace(/</g, "&lt;")}</div>`);
    // contenuto sotto il titolo in un .body centrato in verticale
    if (!centered && !s.querySelector(":scope > .body")) {
      const body = document.createElement("div");
      body.className = "body";
      const keep = (el) => el.matches("h1, .kicker, .sub, .notes, .sticker, .qr.corner, script");
      [...s.children].filter((el) => !keep(el)).forEach((el) => body.appendChild(el));
      // il .sub resta in alto solo se segue il titolo
      s.insertBefore(body, s.querySelector(":scope > .sticker, :scope > .notes"));
    }
    // titoli grandi: parola per parola
    if (centered) {
      s.querySelectorAll(":scope > h1, .lockup").forEach((h) => {
        if (h.querySelector(".w")) return;
        let w = 0;
        const walk = (node) => {
          [...node.childNodes].forEach((n) => {
            if (n.nodeType === 3) {
              const frag = document.createDocumentFragment();
              n.textContent.split(/(\s+)/).forEach((part) => {
                if (!part) return;
                if (/^\s+$/.test(part)) return frag.append(part);
                const span = document.createElement("span");
                span.className = "w";
                span.style.setProperty("--w", w++);
                span.textContent = part;
                frag.append(span);
              });
              n.replaceWith(frag);
            } else if (n.nodeType === 1 && !n.classList.contains("logo")) walk(n);
          });
        };
        walk(h);
      });
    }
    // divisori: il numero della parte davanti al titolo. Da data-n sull'h1 ("off" lo toglie), dal
    // vecchio <span class="n"> o dall'ordine. Solo se il divisore apre davvero una parte: "Domande?"
    // prima della chiusura non ha slide dopo di sé, quindi niente numero
    if (s.classList.contains("section")) {
      const h = s.querySelector(":scope > h1");
      const old = s.querySelector(":scope > .n");
      const after = slides.slice(idx + 1).find((x) => !x.classList.contains("section"));
      const opens = after && !after.classList.contains("thanks") && !after.classList.contains("cover");
      if (opens) partNo++;
      const n = h?.dataset.n ?? old?.textContent.trim() ?? (opens ? String(partNo).padStart(2, "0") : "");
      old?.remove();
      if (h && n && n !== "off" && !h.querySelector(":scope > .n")) h.insertAdjacentHTML("afterbegin", `<span class="n">${n}</span>`);
    }
    // emblema copertina
    // (non se la copertina ha già un'immagine sua a destra: una finestra finta)
    if (s.classList.contains("cover") && !s.classList.contains("brand-only") && !s.querySelector(".orbit, :scope > .window")) {
      s.insertAdjacentHTML("beforeend", '<div class="orbit" aria-hidden="true"><i class="ring r1"></i><i class="ring r2"></i><i class="ring r3"></i><span class="logo"></span></div>');
    }
    // footer e numero
    if (s.dataset.footer !== "off" && !s.classList.contains("cover")) {
      s.insertAdjacentHTML("beforeend", '<div class="slide-foot"><span class="logo"></span>Tesseract</div>');
      const num = String(idx + 1).padStart(2, "0") + (READ ? ` / ${String(total).padStart(2, "0")}` : "");
      if (!centered) s.insertAdjacentHTML("beforeend", `<div class="slide-num">${num}</div>`);
    }
    // animazioni d'ingresso a cascata; nelle righe con icona tessera e testo entrano insieme
    let k = 0;
    const rows = new Map();
    s.querySelectorAll(ANIM).forEach((el) => {
      if (el.closest(".notes") || el.classList.contains("w") || el.classList.contains("reveal")) return;
      if (!el.hasAttribute("data-anim")) el.setAttribute("data-anim", "");
      const row = el.matches(".irows > li > *") ? el.parentElement : null;
      if (row && !rows.has(row)) rows.set(row, k++);
      el.style.setProperty("--i", Math.min(row ? rows.get(row) : k++, 16));
    });
  });

  /* ---------- Componenti ---------- */
  // righe con icona: l'icona dentro una tessera di vetro
  document.querySelectorAll(".irows > li > svg.ico").forEach((svg) => {
    const tile = document.createElement("span");
    tile.className = "tile";
    // l'animazione passa alla tessera di vetro, che deve entrare insieme al testo
    for (const a of ["style", "data-anim"]) if (svg.hasAttribute(a)) (tile.setAttribute(a, svg.getAttribute(a)), svg.removeAttribute(a));
    svg.replaceWith(tile);
    tile.appendChild(svg);
  });
  // colonne esplicite
  document.querySelectorAll("[data-cols]").forEach((el) => el.style.setProperty("--cols", el.dataset.cols));
  // agenda: tessere fino a 9 voci (7-9: tessere compatte su tre colonne), poi righe su due colonne;
  // ogni voce porta alla sezione corrispondente e ne riprende il sottotitolo (voci in più, come "Domande", no)
  document.querySelectorAll(".agenda").forEach((el) => {
    const n = el.children.length;
    if (n > 9) {
      el.classList.add("long");
      el.style.setProperty("--rows", Math.ceil(n / 2));
    } else {
      if (n > 6) el.classList.add("dense");
      if (!el.dataset.cols) el.style.setProperty("--cols", n > 4 ? 3 : n);
      [...el.children].forEach((li, i) => li.insertAdjacentHTML("afterbegin", `<span class="num">${String(i + 1).padStart(2, "0")}</span>`));
    }
    [...el.children].forEach((li, i) => {
      if (!sections[i]) return;
      const { start, sub } = sections[i];
      if (start) li.setAttribute("data-goto", slides.indexOf(start));
      if (n <= 9 && sub && !li.querySelector("small")) li.insertAdjacentHTML("beforeend", `<small>${sub}</small>`);
    });
  });
  // numeri a contorno (divisori, indice): un SVG sopra il testo, così il contorno si può tracciare.
  // Il testo resta (trasparente) per l'impaginazione; la linea di base si misura con un elemento sonda.
  document.fonts.ready.then(() => {
    // disegni che dipendono dall'impaginazione (posizioni dei riquadri): a font caricati
    document.querySelectorAll(".map").forEach(drawMap);
    document.querySelectorAll(".road").forEach(drawRoad);
    document.querySelectorAll(".window > .scroll").forEach(settleScroll);
    // <mark> diviso in parole: un solo gradiente su tutta l'evidenziazione (vedi theme.css)
    document.querySelectorAll("mark").forEach((m) => {
      const ws = [...m.querySelectorAll(".w")];
      if (!ws.length) return;
      const left = Math.min(...ws.map((w) => w.offsetLeft));
      const right = Math.max(...ws.map((w) => w.offsetLeft + w.offsetWidth));
      m.style.setProperty("--gw", `${right - left}px`);
      ws.forEach((w) => w.style.setProperty("--gx", `${w.offsetLeft - left}px`));
    });
    document.querySelectorAll(".slide.section > h1 > .n, .agenda > li > .num").forEach((el) => {
      if (el.querySelector("svg.draw")) return;
      const probe = document.createElement("i");
      probe.style.cssText = "display:inline-block;width:0;height:0;vertical-align:baseline";
      el.append(probe);
      const base = probe.offsetTop;
      probe.remove();
      const NS = "http://www.w3.org/2000/svg";
      const svg = document.createElementNS(NS, "svg");
      svg.setAttribute("class", "draw");
      svg.setAttribute("aria-hidden", "true");
      const text = document.createElementNS(NS, "text");
      text.setAttribute("x", "0");
      text.setAttribute("y", base);
      text.textContent = el.textContent.trim();
      svg.appendChild(text);
      el.appendChild(svg);
      el.classList.add("outlined");
    });
  });
  document.addEventListener("click", (e) => {
    const li = e.target.closest("[data-goto]");
    if (li && !root.classList.contains("overview")) (e.preventDefault(), go(+li.dataset.goto));
  });
  // barre: data-value
  // data-scale="max" sul contenitore: la barra più lunga riempie la riga, le altre in proporzione
  // (per confrontare voci tra loro, non per un avanzamento su 100) e il valore sta in fondo alla barra
  // data-compare="Noi|Riferimento" sul contenitore: ogni voce ha due barre, data-value (la nostra) e
  // data-vs (il riferimento, più sottile e grigia), sulla stessa scala; sopra la legenda
  document.querySelectorAll(".bars[data-compare]").forEach((c) => {
    const bars = [...c.querySelectorAll(":scope > .bar")];
    const num = (x) => parseFloat(x || "0");
    const max = Math.max(...bars.flatMap((b) => [num(b.dataset.value), num(b.dataset.vs)]), 1);
    const [a, b2] = c.dataset.compare.split("|");
    if (!c.querySelector(":scope > .key")) c.insertAdjacentHTML("afterbegin", `<p class="key"><span>${a}</span><span class="ref">${b2 || ""}</span></p>`);
    bars.forEach((b) => {
      if (b.querySelector(".pair")) return;
      const v = num(b.dataset.value), r = num(b.dataset.vs);
      b.innerHTML = `<span>${b.innerHTML}</span><span class="pair">` +
        `<i style="--v:${(v / max) * 100}"><em>${b.dataset.label || v + "%"}</em></i>` +
        `<i class="ref" style="--v:${(r / max) * 100}"><em>${b.dataset.vsLabel || r + "%"}</em></i></span>`;
    });
  });
  document.querySelectorAll(".bars:not([data-compare])").forEach((c) => {
    const bars = [...c.querySelectorAll(":scope > .bar")];
    const rel = c.dataset.scale === "max";
    const max = Math.max(...bars.map((b) => parseFloat(b.dataset.value || "0")), 1);
    bars.forEach((b) => {
      const v = parseFloat(b.dataset.value || "0");
      b.style.setProperty("--v", rel ? (v / max) * 100 : Math.max(0, Math.min(100, v)));
      if (!b.querySelector("i")) {
        const label = b.innerHTML;
        const em = `<em>${b.dataset.label || v + "%"}</em>`;
        b.innerHTML = rel ? `<span>${label}</span><i>${em}</i>` : `<span>${label}</span><i></i>${em}`;
      }
    });
  });
  // 5x1000: il codice fiscale in caselle, una per cifra (il testo copiato resta il codice intero)
  document.querySelectorAll(".fivex .code > b").forEach((b) => {
    const code = b.textContent.replace(/\s+/g, "");
    if (!/^\d{6,16}$/.test(code) || b.querySelector("span")) return;
    b.setAttribute("aria-label", code);
    b.innerHTML = [...code].map((d) => `<span>${d}</span>`).join("");
  });
  // colonne: altezze relative al valore più alto del grafico; data-from = parte "prima"
  document.querySelectorAll(".timeline").forEach((tl) => tl.style.setProperty("--n", tl.children.length));
  document.querySelectorAll(".columns").forEach((c) => {
    const cols = [...c.querySelectorAll(":scope > .col")];
    const num = (x) => parseFloat(x || "0");
    const max = Math.max(...cols.map((col) => num(col.dataset.value)), 1);
    const desc = [];
    cols.forEach((col, i) => {
      const v = num(col.dataset.value);
      col.style.setProperty("--h", v / max);
      col.style.setProperty("--i", i);
      if (col.dataset.from) col.style.setProperty("--b", Math.min(1, num(col.dataset.from) / (v || 1)));
      if (!col.querySelector("i")) {
        const name = col.innerHTML;
        // etichette accanto alla colonna: la cifra grande, il resto del testo piccolo sotto
        const side = (text, cls) => {
          if (!text) return "";
          const [, n, note] = text.trim().match(/^(\S+)\s*(.*)$/);
          return `<b${cls ? ` class="${cls}"` : ""}>${n}${note ? `<small>${note}</small>` : ""}</b>`;
        };
        const sides = side(col.dataset.delta) + side(col.dataset.from && col.dataset.fromLabel, "base");
        col.innerHTML = `<em>${col.dataset.label || v}</em><i></i><span>${name}</span>${sides}`;
      }
      desc.push(`${col.querySelector("span").textContent}: ${col.dataset.label || v}`);
    });
    c.setAttribute("role", "img");
    c.setAttribute("aria-label", desc.join(", "));
  });
  // crescita: --b = valore di partenza / valore di oggi
  document.querySelectorAll(".growth").forEach((g) => {
    const from = parseFloat(g.dataset.from || "0"), v = parseFloat(g.dataset.value || "0");
    if (v > 0) g.style.setProperty("--b", Math.min(1, Math.max(0, from / v)));
  });
  // card a gruppi: ogni p.group apre una fila; le card del gruppo si dividono la riga (12 colonne)
  document.querySelectorAll(".cards").forEach((c) => {
    if (!c.querySelector(":scope > .group")) return;
    c.classList.add("grouped");
    let group = [], muted = false;
    const flush = () => {
      const per = Math.min(group.length, 4) || 1;
      group.forEach((el) => el.style.setProperty("--span", 12 / per));
      group = [];
    };
    [...c.children].forEach((el) => {
      if (el.matches(".group")) return flush(), (muted = el.classList.contains("muted"));
      if (muted) el.classList.add("muted");
      group.push(el);
    });
    flush();
  });
  // interfacce finte: il testo che scorre in un contenitore, la casella da spuntare, il puntatore
  document.querySelectorAll(".window > .scroll").forEach((sc) => {
    if (sc.querySelector(":scope > div")) return;
    const inner = document.createElement("div");
    inner.append(...sc.childNodes);
    sc.append(inner);
  });
  document.querySelectorAll("p.check").forEach((p) => {
    if (p.querySelector(".box")) return;
    const text = document.createElement("span");
    text.append(...p.childNodes);
    p.append(text);
    p.insertAdjacentHTML("afterbegin", '<span class="box"><svg viewBox="0 0 16 16" aria-hidden="true"><path pathLength="1" d="M3 8.5 6.5 12 13 4.5"/></svg></span>');
  });
  document.querySelectorAll(".btn.click").forEach((b) => {
    if (!b.querySelector(".cursor")) b.insertAdjacentHTML("beforeend", '<svg class="cursor" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 2.5 4 19.5 8.6 15.2 11.6 22 14.7 20.6 11.8 14 18 14Z"/></svg>');
  });
  // il testo che scorre si ferma con il <mark class="flash"> (o l'ultimo paragrafo) al centro
  function settleScroll(sc) {
    const inner = sc.firstElementChild;
    const m = inner?.querySelector("mark.flash") || inner?.lastElementChild;
    if (!m || sc.dataset.scroll === "manual") return;
    const max = Math.max(0, inner.offsetHeight - sc.clientHeight);
    const want = m.offsetTop + m.offsetHeight / 2 - sc.clientHeight / 2;
    sc.style.setProperty("--scroll", `${-Math.round(Math.max(0, Math.min(max, want)))}px`);
  }
  // percorso a serpente: prima fila da sinistra a destra, seconda da destra a sinistra (sfalsata di
  // mezzo passo se ha un passo in meno); numeri nei pallini
  document.querySelectorAll(".road").forEach((road) => {
    const items = [...road.querySelectorAll(":scope > li")];
    const top = Math.ceil(items.length / 2), bot = items.length - top;
    road.style.setProperty("--rc", top * 2);
    items.forEach((li, i) => {
      if (!li.querySelector(":scope > .dot")) li.insertAdjacentHTML("afterbegin", `<span class="dot">${i + 1}</span>`);
      const j = i - top;
      const col = i < top ? 2 * i + 1 : bot === top ? 2 * (top - 1 - j) + 1 : 2 * (top - 1 - j);
      li.style.gridColumn = `${col} / span 2`;
      li.style.gridRow = i < top ? 1 : 2;
    });
  });
  const SVGNS = "http://www.w3.org/2000/svg";
  const TIP = "M-11,-5.5 L0,0 L-11,5.5 Q-8,0 -11,-5.5 z";
  function drawRoad(road) {
    const items = [...road.querySelectorAll(":scope > li")];
    if (!items.length) return;
    const dots = items.map((li) => {
      const d = li.querySelector(":scope > .dot");
      return { li, x: li.offsetLeft + d.offsetLeft + d.offsetWidth / 2, y: li.offsetTop + d.offsetTop + d.offsetHeight / 2 };
    });
    const top = Math.ceil(items.length / 2);
    const y1 = dots[0].y, x0 = dots[0].x - 150;
    let d, total, at, end, dir;
    if (dots.length > top) {
      const y2 = dots[top].y, r = (y2 - y1) / 2;
      const xr = Math.max(...dots.map((p) => p.x)) + 40;
      const xe = dots.at(-1).x - 130;
      d = `M${x0},${y1} L${xr},${y1} A${r},${r} 0 0 1 ${xr},${y2} L${xe},${y2}`;
      total = xr - x0 + Math.PI * r + (xr - xe);
      at = (p, i) => (i < top ? p.x - x0 : xr - x0 + Math.PI * r + (xr - p.x));
      (end = [xe, y2]), (dir = 180);
    } else {
      const xe = dots.at(-1).x + 130;
      d = `M${x0},${y1} L${xe},${y1}`;
      total = xe - x0;
      at = (p) => p.x - x0;
      (end = [xe, y1]), (dir = 0);
    }
    const T0 = 300, DUR = 2400;
    dots.forEach((p, i) => p.li.style.setProperty("--d", `${Math.round(T0 + (DUR * at(p, i)) / total - 120)}ms`));
    let svg = road.querySelector(":scope > svg");
    if (!svg) {
      svg = document.createElementNS(SVGNS, "svg");
      svg.setAttribute("aria-hidden", "true");
      road.prepend(svg);
    }
    svg.innerHTML =
      '<defs><linearGradient id="road-grad" x1="0" x2="1"><stop offset="0" style="stop-color:var(--blue-3)"/><stop offset="1" style="stop-color:var(--blue-2)"/></linearGradient></defs>' +
      `<path class="track" pathLength="1" style="--d:${T0}ms;--dur:${DUR}ms" d="${d}"/>` +
      `<path class="tip" style="--d:${T0 + DUR - 100}ms" transform="translate(${end[0] - (dir ? 12 : -12)},${end[1]}) rotate(${dir}) scale(2)" d="${TIP}"/>` +
      `<path class="pulse" pathLength="1" style="--d:${T0 + DUR + 400}ms" d="${d}"/>`;
  }
  // mappa a colonne: una freccia per ogni id in data-to; le frecce che escono da un riquadro (o ci
  // entrano) si aprono a ventaglio, ordinate per non incrociarsi; colore dal filone (data-track)
  function drawMap(map) {
    const nodes = [...map.querySelectorAll(":scope > .col > .node")];
    const cols = [...map.querySelectorAll(":scope > .col")];
    const byId = new Map(nodes.filter((n) => n.dataset.id).map((n) => [n.dataset.id, n]));
    const box = new Map(nodes.map((n) => {
      const c = n.parentElement, x = c.offsetLeft + n.offsetLeft, y = c.offsetTop + n.offsetTop;
      return [n, { l: x, r: x + n.offsetWidth, h: n.offsetHeight, cy: y + n.offsetHeight / 2, col: cols.indexOf(c) }];
    }));
    const STEP = 700;
    nodes.forEach((n) => n.style.setProperty("--d", `${box.get(n).col * STEP + [...n.parentElement.children].indexOf(n) * 60}ms`));
    const links = [];
    nodes.forEach((a) => (a.dataset.to || "").split(/\s+/).forEach((id) => byId.has(id) && links.push({ a, b: byId.get(id) })));
    const fan = (key, other, end) => {
      nodes.forEach((n) => {
        const own = links.filter((l) => l[key] === n).sort((p, q) => box.get(p[other]).cy - box.get(q[other]).cy);
        const bx = box.get(n), step = Math.min(18, (bx.h * 0.6) / Math.max(own.length - 1, 1));
        own.forEach((l, i) => (l[end] = bx.cy + (i - (own.length - 1) / 2) * step));
      });
    };
    fan("a", "b", "y1");
    fan("b", "a", "y2");
    let svg = map.querySelector(":scope > svg.links");
    if (!svg) {
      svg = document.createElementNS(SVGNS, "svg");
      svg.setAttribute("class", "links");
      svg.setAttribute("aria-hidden", "true");
      map.prepend(svg);
    }
    const last = (cols.length - 1) * STEP;
    svg.innerHTML = links.map((l, i) => {
      const A = box.get(l.a), B = box.get(l.b);
      const x1 = A.r, x2 = B.l - 10, mx = (x1 + x2) / 2;
      const track = l.a.dataset.track || l.b.dataset.track;
      const t = track ? `--t:var(--t${track});` : "";
      const d = `M${x1},${l.y1} C${mx},${l.y1} ${mx},${l.y2} ${x2},${l.y2}`;
      const d0 = A.col * STEP + 250;
      return `<path class="line" pathLength="1" style="${t}--d:${d0}ms;--dur:${STEP}ms" d="${d}"/>` +
        `<path class="tip" style="${t}--d:${d0 + STEP - 120}ms" transform="translate(${B.l},${l.y2})" d="${TIP}"/>` +
        `<path class="pulse" pathLength="1" style="${t}--d:${last + 900 + i * 290}ms" d="${d}"/>`;
    }).join("");
  }
  // rimandi: <a data-ref="id"></a> diventa il numero della slide che contiene l'id e ci porta
  // (anche nel PDF: il link punta all'id)
  document.querySelectorAll("[data-ref]").forEach((el) => {
    const target = document.getElementById(el.dataset.ref);
    const i = slides.indexOf(target?.closest(".slide"));
    if (i < 0) return el.classList.add("ref-missing");
    if (!el.textContent.trim()) el.textContent = String(i + 1);
    el.dataset.goto = i;
    if (el.tagName === "A") el.setAttribute("href", `#${el.dataset.ref}`);
  });
  // nuvola: posti attorno al titolo, riempiti in modo bilanciato (max 16)
  const SLOTS = [
    [24, 32], [76, 66], [56, 10], [40, 90], [76, 32], [24, 66], [30, 12], [64, 88],
    [7, 49], [93, 49], [82, 11], [16, 88], [9, 22], [90, 86], [93, 22], [8, 76],
  ];
  document.querySelectorAll(".cloud").forEach((c) => {
    const items = [...c.querySelectorAll(":scope > span")];
    items.forEach((el, i) => {
      if (!el.style.getPropertyValue("--x")) {
        const [x, y] = SLOTS[i % SLOTS.length];
        const j = ((i * 37) % 7) - 3;
        el.style.setProperty("--x", `${x + j * 0.5}%`);
        el.style.setProperty("--y", `${y - j * 0.6}%`);
      }
      el.style.setProperty("--d", `${-(i * 0.7) % 6}s`);
      if (!el.querySelector(":scope > i")) el.innerHTML = `<i>${el.innerHTML}</i>`;
    });
  });
  // votazione: clic = +1, Maiusc+clic = −1
  document.querySelectorAll(".vote > button").forEach((btn) => {
    const out = btn.querySelector("b") || btn.appendChild(document.createElement("b"));
    if (!out.textContent.trim()) out.textContent = "0";
    btn.classList.add("glass");
    btn.addEventListener("click", (e) => {
      const v = Math.max(0, (parseInt(out.textContent, 10) || 0) + (e.shiftKey ? -1 : 1));
      out.textContent = v;
    });
  });
  // immagini mancanti → segnaposto con il nome del file
  const placeholder = (el, src, label) => {
    const ph = document.createElement("div");
    ph.className = `ph ${el.className}`.trim();
    ph.innerHTML = `${icon("camera")}<span>${label || T.image}</span><span>${src}</span>`;
    for (const a of ["style", "data-anim"]) if (el.hasAttribute(a)) ph.setAttribute(a, el.getAttribute(a));
    el.replaceWith(ph);
  };
  document.querySelectorAll("img").forEach((img) => {
    const src = img.getAttribute("src");
    const fail = () => placeholder(img, src || "?", img.alt);
    if (!src) return fail();
    if (img.complete && img.naturalWidth === 0 && !src.startsWith("data:")) fail();
    else img.addEventListener("error", fail, { once: true });
  });
  // numeri che contano fino al valore
  // numeri che contano fino al valore: ogni numero del testo ("7", "0–4", "20 000+"); i decimali restano fermi
  const counters = [...document.querySelectorAll(".stats b, .num[data-count], .cloud b, .growth > p > b")].map((el) => {
    const final = el.textContent, parts = final.split(/(\d[\d.,\s  ]*\d|\d)/);
    if (parts.some((p, i) => i % 2 && /^\d{1,3}[.,]\d{1,2}$/.test(p.trim()))) return null; // "3,8/5", "4.5"
    const nums = parts.map((p, i) => {
      if (!(i % 2)) return null;
      const sep = (p.match(/[.,\s  ]/) || [""])[0];
      return { value: parseInt(p.replace(/\D/g, ""), 10), fmt: (v) => String(v).replace(/\B(?=(\d{3})+(?!\d))/g, sep) };
    });
    const max = Math.max(...nums.filter(Boolean).map((n) => n.value));
    return Number.isFinite(max) ? { el, parts, nums, final, max } : null;
  }).filter(Boolean);
  function runCounters(slide) {
    counters.forEach((c) => {
      if (!slide.contains(c.el)) return;
      if (STATIC) return (c.el.textContent = c.final);
      // i numeri piccoli si contano uno per uno, più in fretta; quelli grandi in 1,4 s
      const t0 = performance.now() + 250, dur = c.max < 10 ? 300 + c.max * 160 : 1400;
      const tick = (t) => {
        if (printing) return (c.el.textContent = c.final);
        const p = Math.min(1, Math.max(0, (t - t0) / dur));
        const e = c.max < 10 ? p : 1 - Math.pow(1 - p, 3);
        c.el.textContent = p >= 1 ? c.final : c.parts.map((s, i) => (c.nums[i] ? c.nums[i].fmt(Math.floor(c.nums[i].value * e)) : s)).join("");
        if (p < 1 && slide.classList.contains("active")) requestAnimationFrame(tick);
        else c.el.textContent = c.final;
      };
      requestAnimationFrame(tick);
    });
  }
  // codice del 5x1000: ogni cifra gira come un contatore e si ferma, una dopo l'altra
  function rollDigits(slide) {
    slide.querySelectorAll(".fivex .code > b").forEach((b) => {
      const spans = [...b.querySelectorAll(":scope > span")];
      spans.forEach((sp, i) => {
        const final = (sp.dataset.d ??= sp.textContent);
        if (STATIC) return (sp.textContent = final);
        const t0 = performance.now(), dur = 1700 + i * 130; // il riquadro entra dopo ~1 s: il rullo deve vedersi
        let last = 0;
        const tick = (t) => {
          if (printing || !slide.classList.contains("active") || t - t0 >= dur) return (sp.textContent = final);
          if (t - last > 55) (last = t), (sp.textContent = String(Math.floor(Math.random() * 10)));
          requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    });
  }
  // stampa / PDF. Firefox fotografa la pagina con le animazioni ferme dove sono (titoli sbiaditi,
  // riquadri a metà ingresso) prima di applicare @media print; e sfondo e vetro di stampa
  // (--bg-print, --bg-frost) sono immagini che a schermo non si usano: se il browser non le ha
  // ancora decodificate, nel PDF mancano. Quindi prima di stampare: modalità statica (tutto al suo
  // stato finale), numeri e cifre al valore finale, immagini pronte. Dopo, la modalità di prima.
  let printing = false;
  let wasStatic;
  function settleForPrint() {
    printing = true;
    if (wasStatic === undefined) wasStatic = root.classList.contains("static");
    root.classList.add("static");
    counters.forEach((c) => (c.el.textContent = c.final));
    document.querySelectorAll(".fivex .code > b > span[data-d]").forEach((sp) => (sp.textContent = sp.dataset.d));
    document.querySelectorAll(".map").forEach(drawMap);
    document.querySelectorAll(".road").forEach(drawRoad);
    document.querySelectorAll(".window > .scroll").forEach(settleScroll);
    void document.body.offsetHeight; // applica gli stili prima che il browser acquisisca la pagina
    // animazioni sopravvissute alla modalità statica (non CSS): allo stato finale
    document.getAnimations?.().forEach((a) => a.effect?.getComputedTiming().endTime !== Infinity && a.finish());
  }
  function restoreAfterPrint() {
    printing = false;
    if (wasStatic === undefined) return;
    root.classList.toggle("static", wasStatic);
    wasStatic = undefined;
  }
  addEventListener("beforeprint", settleForPrint); // anche la stampa dal menu del browser
  addEventListener("afterprint", restoreAfterPrint);
  // le immagini della stampa si decodificano una volta sola, a pagina caricata: pronte anche per
  // la stampa dal menu. Restano in printImgs, se no il browser le butta.
  let printImgs, printReady;
  function preparePrint() {
    if (printReady) return printReady;
    const css = getComputedStyle(root);
    const urls = ["--bg-print", "--bg-frost"].flatMap((v) => [...css.getPropertyValue(v).matchAll(/url\((["']?)(.*?)\1\)/g)].map((m) => m[2]));
    printImgs = [...urls.map((src) => Object.assign(new Image(), { src })), ...document.images];
    return (printReady = Promise.all(printImgs.map((img) => img.decode().catch(() => {}))).then(() => document.fonts.ready));
  }
  if (!EMBED && !PRESENTER) {
    const idle = () => (window.requestIdleCallback || setTimeout)(preparePrint);
    document.readyState === "complete" ? idle() : addEventListener("load", idle, { once: true });
  }

  /* ---------- Interfaccia ---------- */
  document.body.insertAdjacentHTML(
    "beforeend",
    `<div class="progress" id="pn-progress"></div>
     <nav class="ui" aria-label="Navigazione">
       <button id="pn-prev" title="${T.prev}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg></button>
       <span class="counter" id="pn-counter"></span>
       <button id="pn-next" title="${T.next}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"/></svg></button>
       <button id="pn-grid" title="${T.grid} (O)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg></button>
       <button id="pn-print" title="${T.print} (S)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9V3h12v6"/><rect x="3" y="9" width="18" height="8" rx="2"/><path d="M6 14h12v7H6z"/></svg></button>
       <button id="pn-fs" title="${T.full} (F)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M8 3H5a2 2 0 0 0-2 2v3M21 8V5a2 2 0 0 0-2-2h-3M3 16v3a2 2 0 0 0 2 2h3M16 21h3a2 2 0 0 0 2-2v-3"/></svg></button>
     </nav>`,
  );
  if (EMBED) document.querySelector(".ui").hidden = true;

  /* ---------- Navigazione ---------- */
  let cur = 0;
  let presenterWin = null;
  const shapes = [...document.querySelectorAll(".bg .shape")];
  const wire = document.querySelector(".bg .wire");
  const revealsOf = (s) => [...s.querySelectorAll(".reveal")];

  function moveBg(i) {
    shapes.forEach((b, k) => {
      const x = Math.sin(i * 1.1 + k * 1.7) * 7;
      const y = Math.cos(i * 0.8 + k * 2.3) * 6;
      const r = Math.sin(i * 0.5 + k) * 10;
      b.style.transform = `translate(${x}vw, ${y}vh) rotate(${r}deg)`;
    });
    if (wire) wire.style.transform = `translate(${Math.sin(i * 0.6) * 2}%, ${Math.cos(i * 0.5) * 1.5}%) rotate(${Math.sin(i * 0.4) * 3}deg)`;
  }

  /* ---------- animazioni sulla slide: data-fx="…" (uno o più nomi separati da spazi) ----------
     Su tela (disegnate qui): fireworks, confetti (una volta, all'arrivo); network, code, wings (dietro al
     contenuto); pizza, emoji (in mezzo: sopra le foto, sotto le scritte); likes, questions, snake (davanti). train: le persone si
     scambiano di posto in giro. Solo CSS (theme.css): float, wave, pulse,
     flow, shine, wiggle. Spente in ?check/?static/anteprima, nel PDF e con "riduci movimento". */
  const motionPreference = matchMedia("(prefers-reduced-motion: reduce)");
  let REDUCED = motionPreference.matches;
  motionPreference.addEventListener("change", (event) => {
    REDUCED = event.matches;
    if (slides[cur]) runFx(slides[cur]);
  });
  const FX_COLORS = ["#9b1b30", "#701526", "#b23b4d", "#ce8994", "#ffffff"]; // blu del tema e bianco
  const rnd = (a, b) => a + Math.random() * (b - a);
  const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];
  // rettangolo di un elemento della slide in coordinate 1600×900 (null se non c'è)
  function rectOf(slide, sel) {
    const el = slide.querySelector(sel);
    if (!el) return null;
    const s = slide.getBoundingClientRect(), r = el.getBoundingClientRect(), k = 1600 / s.width;
    return { x: (r.left - s.left) * k, y: (r.top - s.top) * k, w: r.width * k, h: r.height * k };
  }
  // posto per un nuovo elemento, condiviso tra gli effetti della stessa slide (es. questions e pizza):
  // tra 24 posti a caso validi sceglie il più lontano da quelli usati negli ultimi 3 s, così si
  // distribuiscono in modo uniforme e non spuntano uno sopra l'altro
  function freeSpot(slide, ok) {
    const now = performance.now();
    slide._spots = (slide._spots || []).filter((s) => now - s.t < 3000);
    let best = null, bd = -1;
    for (let i = 0; i < 24; i++) {
      const x = rnd(80, 1520), y = rnd(170, 830);
      if (!ok(x, y)) continue;
      const d = Math.min(Infinity, ...slide._spots.map((s) => Math.hypot(s.x - x, s.y - y)));
      if (d > bd) (bd = d), (best = { x, y });
    }
    if (best) slide._spots.push({ ...best, t: now });
    return best;
  }
  // fuori dal centro della slide (titolo) e lontano dallo sticker
  const awayFromCenter = (slide) => {
    const st = rectOf(slide, ".sticker");
    return (x, y) => !(x > 420 && x < 1180 && y > 280 && y < 620) && !(st && x > st.x - 70 && x < st.x + st.w + 70 && y > st.y - 70 && y < st.y + st.h + 70);
  };
  const FX = {
    // cinque fuochi bianchi e blu, in alto e lontano dal titolo
    fireworks() {
      const bursts = [[1180, 230, 500], [760, 300, 1000], [1400, 360, 1450], [980, 170, 1900], [560, 260, 2400]];
      const sparks = [];
      let fired = 0;
      return (ctx, ms, k) => {
        bursts.forEach(([x, y, at], i) => {
          const p = (ms - at + 500) / 500; // razzo che sale nei 500 ms prima dell'esplosione
          if (i < fired || p < 0 || p >= 1) return;
          ctx.globalAlpha = 0.9;
          ctx.fillStyle = "#9b1b30";
          ctx.fillRect(x - 1.5, 900 - (900 - y) * (1 - (1 - p) ** 2), 3, 18);
        });
        while (fired < bursts.length && ms >= bursts[fired][2]) {
          const [x, y] = bursts[fired++], main = FX_COLORS[fired % FX_COLORS.length];
          for (let i = 0; i < 90; i++) {
            const a = (i / 90) * Math.PI * 2 + rnd(0, 0.2), v = rnd(3, 7.5);
            sparks.push({ x, y, vx: Math.cos(a) * v, vy: Math.sin(a) * v, life: 1, c: Math.random() < 0.7 ? main : pick(FX_COLORS) });
          }
        }
        for (const s of sparks) {
          s.vx *= 0.965 ** k;
          s.vy = s.vy * 0.965 ** k + 0.06 * k;
          s.x += s.vx * k;
          s.y += s.vy * k;
          s.life -= 0.011 * k;
          if (s.life <= 0) continue;
          ctx.globalAlpha = Math.min(1, s.life * 1.4);
          ctx.fillStyle = s.c;
          ctx.beginPath();
          ctx.arc(s.x, s.y, 3.2, 0, Math.PI * 2);
          ctx.fill();
        }
        return fired < bursts.length || sparks.some((s) => s.life > 0);
      };
    },
    // coriandoli bianchi e blu che cadono dall'alto e girano
    confetti() {
      const bits = Array.from({ length: 150 }, () => ({
        x: rnd(0, 1600), y: rnd(-260, -20), vy: rnd(2.2, 4.2), sway: rnd(0, 6.28), sp: rnd(0.02, 0.05),
        rot: rnd(0, 6.28), vr: rnd(-0.12, 0.12), w: rnd(9, 15), h: rnd(14, 22), c: pick(FX_COLORS), at: rnd(0, 1300),
      }));
      return (ctx, ms, k) => {
        let alive = false;
        for (const b of bits) {
          if (ms < b.at || b.y > 940) continue;
          alive = true;
          b.sway += b.sp * k;
          b.y += b.vy * k;
          b.x += Math.sin(b.sway) * 1.4 * k;
          b.rot += b.vr * k;
          ctx.save();
          ctx.translate(b.x, b.y);
          ctx.rotate(b.rot);
          ctx.scale(1, Math.cos(b.sway * 2)); // il foglietto si gira mentre cade
          ctx.globalAlpha = 0.95;
          ctx.fillStyle = b.c;
          if (b.c === "#ffffff") (ctx.shadowColor = "rgb(17 86 174 / 0.35)"), (ctx.shadowBlur = 4);
          ctx.fillRect(-b.w / 2, -b.h / 2, b.w, b.h);
          ctx.restore();
        }
        return alive || ms < 1400;
      };
    },
    // la rete: nodi che si spostano piano e si collegano quando sono vicini (dietro al contenuto)
    network() {
      const nodes = Array.from({ length: 38 }, () => ({
        x: rnd(0, 1600), y: rnd(0, 900), vx: rnd(-0.35, 0.35), vy: rnd(-0.25, 0.25), r: rnd(2.5, 5),
      }));
      const D = 230;
      return (ctx, ms, k) => {
        const fade = Math.min(1, ms / 1200);
        for (const n of nodes) {
          n.x += n.vx * k;
          n.y += n.vy * k;
          if (n.x < -20 || n.x > 1620) n.vx *= -1;
          if (n.y < -20 || n.y > 920) n.vy *= -1;
        }
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = "#9b1b30";
        for (let i = 0; i < nodes.length; i++)
          for (let j = i + 1; j < nodes.length; j++) {
            const a = nodes[i], b = nodes[j], d = Math.hypot(a.x - b.x, a.y - b.y);
            if (d > D) continue;
            ctx.globalAlpha = (1 - d / D) * 0.28 * fade;
            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            ctx.lineTo(b.x, b.y);
            ctx.stroke();
          }
        ctx.fillStyle = "#9b1b30";
        for (const n of nodes) {
          ctx.globalAlpha = 0.45 * fade;
          ctx.beginPath();
          ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
          ctx.fill();
        }
        return true;
      };
    },
    // codice che scende piano, molto tenue (dietro al contenuto): per l'IT
    code() {
      const glyphs = "01{}<>/=;()[]".split("");
      const cols = Array.from({ length: 40 }, (_, i) => ({ x: 20 + i * 40, y: rnd(-900, 0), v: rnd(1.2, 3), acc: 0 }));
      return (ctx, ms, k) => {
        // sfuma quello che c'è già, così resta una scia
        ctx.globalCompositeOperation = "destination-out";
        ctx.globalAlpha = 0.05 * k;
        ctx.fillRect(0, 0, 1600, 900);
        ctx.globalCompositeOperation = "source-over";
        ctx.font = "600 26px ui-monospace, monospace";
        ctx.fillStyle = "#9b1b30";
        for (const c of cols) {
          c.acc += c.v * k;
          if (c.acc < 26) continue;
          c.acc = 0;
          c.y += 26;
          if (c.y > 940) c.y = rnd(-300, 0);
          ctx.globalAlpha = 0.55 * Math.min(1, ms / 1200);
          ctx.fillText(pick(glyphs), c.x, c.y);
        }
        return true;
      };
    },
    // cuori che salgono dal telefono (o dall'immagine) della slide, come i like
    likes(slide) {
      const hearts = [];
      let next = 900;
      const heart = (ctx, s) => {
        ctx.beginPath();
        ctx.moveTo(0, s * 0.3);
        ctx.bezierCurveTo(0, 0, -s * 0.5, 0, -s * 0.5, s * 0.3);
        ctx.bezierCurveTo(-s * 0.5, s * 0.6, 0, s * 0.8, 0, s);
        ctx.bezierCurveTo(0, s * 0.8, s * 0.5, s * 0.6, s * 0.5, s * 0.3);
        ctx.bezierCurveTo(s * 0.5, 0, 0, 0, 0, s * 0.3);
        ctx.fill();
      };
      return (ctx, ms, k) => {
        if (ms > next) {
          next = ms + rnd(220, 480);
          const r = rectOf(slide, ".phone, .media img, .media") || { x: 1200, y: 300, w: 260, h: 520 };
          hearts.push({
            x: r.x + r.w / 2 + rnd(-70, 70), y: r.y + rnd(-10, 50), vx: 0, vy: rnd(1.3, 2.2),
            ph: rnd(0, 6.28), s: rnd(22, 38), life: 1, grow: 1, c: pick(["#9b1b30", "#b23b4d", "#ce8994", "#ffffff"]),
          });
        }
        for (const h of hearts) {
          h.ph += 0.05 * k;
          h.y -= h.vy * k;
          h.x += (h.vx + Math.sin(h.ph) * 0.9) * k;
          if (h.life <= 0) continue;
          ctx.save();
          ctx.translate(h.x, h.y);
          ctx.globalAlpha = Math.min(1, h.life * 1.6);
          ctx.fillStyle = h.c;
          ctx.shadowColor = "rgb(17 86 174 / 0.35)";
          ctx.shadowBlur = 8;
          heart(ctx, h.s);
          ctx.restore();
        }
        for (let i = hearts.length - 1; i >= 0; i--) if (hearts[i].y < -80) hearts.splice(i, 1); // fino a uscire dallo schermo
        return true;
      };
    },
    // faccine a contorno (felice, triste, occhiali, sorpresa, preoccupata, occhiolino) che escono dall'alto della foto
    emoji(slide) {
      const kinds = ["smile", "sad", "glasses", "wow", "worried", "wink", "laugh", "meh"];
      const faces = [];
      let next = 0;
      const face = (ctx, kind, r) => {
        ctx.fillStyle = "rgb(255 255 255 / 0.85)";
        ctx.beginPath();
        ctx.arc(0, 0, r, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        const ex = r * 0.36, ey = -r * 0.22, er = r * 0.09;
        const dot = (x) => (ctx.beginPath(), ctx.arc(x, ey, er, 0, Math.PI * 2), ctx.fillStyle = ctx.strokeStyle, ctx.fill());
        const arc = (y, rad, a0, a1) => (ctx.beginPath(), ctx.arc(0, y, rad, a0, a1), ctx.stroke());
        if (kind === "glasses") {
          ctx.fillStyle = ctx.strokeStyle;
          for (const x of [-ex, ex]) ctx.fillRect(x - r * 0.27, ey - r * 0.14, r * 0.54, r * 0.3);
          ctx.beginPath();
          ctx.moveTo(-ex + r * 0.27, ey);
          ctx.lineTo(ex - r * 0.27, ey);
          ctx.stroke();
        } else if (kind === "wink") {
          dot(-ex);
          ctx.beginPath();
          ctx.moveTo(ex - r * 0.14, ey);
          ctx.lineTo(ex + r * 0.14, ey);
          ctx.stroke();
        } else if (kind === "worried") {
          dot(-ex);
          dot(ex);
          ctx.beginPath(); // sopracciglia in salita verso il centro
          ctx.moveTo(-ex - r * 0.16, ey - r * 0.2);
          ctx.lineTo(-ex + r * 0.14, ey - r * 0.3);
          ctx.moveTo(ex + r * 0.16, ey - r * 0.2);
          ctx.lineTo(ex - r * 0.14, ey - r * 0.3);
          ctx.stroke();
        } else {
          dot(-ex);
          dot(ex);
        }
        if (kind === "sad" || kind === "worried") arc(r * 0.58, r * 0.38, Math.PI * 1.15, Math.PI * 1.85);
        else if (kind === "wow") (ctx.beginPath(), ctx.arc(0, r * 0.35, r * 0.15, 0, Math.PI * 2), ctx.stroke());
        else if (kind === "meh") (ctx.beginPath(), ctx.moveTo(-r * 0.3, r * 0.36), ctx.lineTo(r * 0.3, r * 0.36), ctx.stroke());
        else if (kind === "laugh") {
          ctx.beginPath();
          ctx.moveTo(-r * 0.42, r * 0.12);
          ctx.arc(0, r * 0.12, r * 0.42, 0, Math.PI);
          ctx.closePath();
          ctx.fillStyle = ctx.strokeStyle;
          ctx.fill();
        } else arc(r * 0.05, r * 0.45, Math.PI * 0.2, Math.PI * 0.8);
      };
      return (ctx, ms, k) => {
        if (ms > next) {
          next = ms + rnd(700, 1200);
          // escono dall'alto della foto (la scatola del Welcome kit), come i cuori dal telefono
          const r = rectOf(slide, ".media img, .media > *, .media") || { x: 300, y: 300, w: 400, h: 400 };
          faces.push({
            x: r.x + r.w * rnd(0.12, 0.88), y: r.y + rnd(-10, 40), vy: rnd(1.3, 2.1), ph: rnd(0, 6.28),
            rot: rnd(-0.15, 0.15), r: rnd(26, 42), kind: pick(kinds), c: pick(["#9b1b30", "#b23b4d", "#701526"]),
          });
        }
        for (const f of faces) {
          f.y -= f.vy * k;
          f.ph += 0.05 * k;
          f.x += Math.sin(f.ph) * 0.9 * k;
          ctx.save();
          ctx.translate(f.x, f.y);
          ctx.rotate(f.rot + Math.sin(f.ph) * 0.12);
          ctx.strokeStyle = f.c;
          ctx.lineWidth = Math.max(2.5, f.r * 0.1);
          ctx.lineCap = "round";
          ctx.shadowColor = "rgb(17 86 174 / 0.3)";
          ctx.shadowBlur = 8;
          face(ctx, f.kind, f.r);
          ctx.restore();
        }
        for (let i = faces.length - 1; i >= 0; i--) if (faces[i].y < -80) faces.splice(i, 1); // fino a uscire dallo schermo
        return true;
      };
    },
    // spicchi di pizza disegnati a contorno blu (come le faccine) che spuntano e salgono come i punti di
    // domanda (questions): lontani dal centro della slide e dallo sticker
    pizza(slide) {
      const slices = [];
      let next = 700;
      const slice = (ctx, s) => {
        ctx.fillStyle = "rgb(255 255 255 / 0.85)";
        ctx.beginPath(); // spicchio: punta in basso, crosta curva in alto
        ctx.moveTo(0, s * 0.62);
        ctx.lineTo(-s * 0.46, -s * 0.38);
        ctx.quadraticCurveTo(0, -s * 0.62, s * 0.46, -s * 0.38);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.beginPath(); // bordo interno della crosta
        ctx.moveTo(-s * 0.39, -s * 0.24);
        ctx.quadraticCurveTo(0, -s * 0.44, s * 0.39, -s * 0.24);
        ctx.stroke();
        for (const [x, y, r] of [[-0.14, -0.08, 0.09], [0.15, -0.02, 0.08], [0, 0.24, 0.07]]) {
          ctx.beginPath(); // salame
          ctx.arc(x * s, y * s, r * s, 0, Math.PI * 2);
          ctx.stroke();
        }
      };
      return (ctx, ms, k) => {
        if (ms > next) {
          next = ms + rnd(900, 1500);
          const at = freeSpot(slide, awayFromCenter(slide));
          if (at) slices.push({ x: at.x, y: at.y, s: rnd(60, 84), rot: rnd(-0.5, 0.5), ph: rnd(0, 6.28), life: 1, grow: 0, c: pick(["#9b1b30", "#b23b4d"]) });
        }
        for (const p of slices) {
          p.y -= 0.6 * k;
          p.ph += 0.04 * k;
          p.grow = Math.min(1, p.grow + 0.06 * k);
          p.life -= 0.006 * k;
          if (p.life <= 0) continue;
          ctx.save();
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rot + Math.sin(p.ph) * 0.1);
          ctx.scale(p.grow, p.grow);
          ctx.globalAlpha = Math.min(1, p.life * 2);
          ctx.strokeStyle = p.c;
          ctx.lineWidth = 4;
          ctx.lineCap = ctx.lineJoin = "round";
          ctx.shadowColor = "rgb(17 86 174 / 0.25)";
          ctx.shadowBlur = 8;
          slice(ctx, p.s);
          ctx.restore();
        }
        for (let i = slices.length - 1; i >= 0; i--) if (slices[i].life <= 0) slices.splice(i, 1);
        return true;
      };
    },
    // punti di domanda bianchi e blu che spuntano qua e là e salgono, lontano dal titolo al centro
    questions(slide) {
      const marks = [];
      let next = 400;
      return (ctx, ms, k) => {
        if (ms > next) {
          next = ms + rnd(350, 700);
          const at = freeSpot(slide, awayFromCenter(slide));
          if (at) marks.push({ x: at.x, y: at.y, s: rnd(46, 90), rot: rnd(-0.35, 0.35), ph: rnd(0, 6.28), life: 1, grow: 0, white: Math.random() < 0.45 });
        }
        for (const m of marks) {
          m.y -= 0.6 * k;
          m.ph += 0.04 * k;
          m.grow = Math.min(1, m.grow + 0.06 * k);
          m.life -= 0.006 * k;
          if (m.life <= 0) continue;
          ctx.save();
          ctx.translate(m.x, m.y);
          ctx.rotate(m.rot + Math.sin(m.ph) * 0.1);
          ctx.scale(m.grow, m.grow);
          ctx.globalAlpha = Math.min(1, m.life * 2);
          ctx.font = `700 ${m.s}px "DM Sans", system-ui, sans-serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.lineJoin = "round";
          ctx.lineWidth = m.s * 0.07;
          ctx.strokeStyle = "#9b1b30";
          ctx.fillStyle = m.white ? "#ffffff" : pick(["#9b1b30", "#b23b4d"]);
          if (m.white) (ctx.shadowColor = "rgb(17 86 174 / 0.3)"), (ctx.shadowBlur = 8);
          ctx.fillText("?", 0, 0);
          if (m.white) ctx.strokeText("?", 0, 0);
          ctx.restore();
        }
        for (let i = marks.length - 1; i >= 0; i--) if (marks[i].life <= 0) marks.splice(i, 1);
        return true;
      };
    },
    // ali bianche che battono ai lati dell'immagine (la lattina "che mette le ali"): dietro all'immagine
    wings(slide) {
      const wing = (ctx, side, flap) => {
        ctx.save();
        ctx.scale(side, 1);
        ctx.rotate(-0.25 + flap);
        ctx.fillStyle = "#ffffff";
        ctx.strokeStyle = "#9b1b30";
        ctx.lineWidth = 5;
        ctx.lineJoin = "round";
        // tre piume, dalla più lunga alla più corta
        for (const [len, ang, wd] of [[230, -0.55, 50], [190, -0.2, 44], [145, 0.15, 38]]) {
          ctx.save();
          ctx.rotate(ang);
          ctx.beginPath();
          ctx.ellipse(len / 2, 0, len / 2, wd / 2, 0, 0, Math.PI * 2);
          ctx.fill();
          ctx.stroke();
          ctx.restore();
        }
        ctx.restore();
      };
      return (ctx, ms) => {
        const el = slide.querySelector(".media img, .media > *"), r = rectOf(slide, ".media img, .media > *");
        if (!r) return false;
        // le ali seguono l'inclinazione dell'immagine (tilt): ruotate attorno al suo centro, attaccate ai suoi bordi
        const rot = (parseFloat(getComputedStyle(el).rotate) || 0) * (Math.PI / 180);
        const w = el.offsetWidth, h = el.offsetHeight, flap = Math.sin(ms * 0.0055) * 0.3;
        // compaiono insieme all'immagine (stessa opacità durante l'ingresso) e la seguono mentre fluttua
        ctx.globalAlpha = parseFloat(getComputedStyle(el).opacity) || 0;
        ctx.shadowColor = "rgb(17 86 174 / 0.3)";
        ctx.shadowBlur = 12;
        ctx.translate(r.x + r.w / 2, r.y + r.h / 2);
        ctx.rotate(rot);
        for (const side of [-1, 1]) {
          ctx.save();
          ctx.translate(side * w * 0.36, -h * 0.14);
          wing(ctx, side, flap);
          ctx.restore();
        }
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        return true;
      };
    },
  };
  // train: le persone delle righe .people (es. 4 sopra e 3 sotto) scivolano su una pista e ci girano
  // sopra piano, a distanze uguali lungo il percorso: sempre tutte visibili, mai sovrapposte.
  const TRAIN_SLOT_MS = 4500; // tempo per passare dal posto di una persona a quello della successiva
  function rotatePeople(slide) {
    const rows = [...slide.querySelectorAll(".people")];
    // in senso orario: prima riga da sinistra, seconda da destra…
    const order = rows.flatMap((r, i) => {
      const p = [...r.querySelectorAll(":scope > .person")];
      return i % 2 ? p.reverse() : p;
    });
    if (order.length < 2) return;
    cancelAnimationFrame(slide._train);
    let home = null, ring = null, len = 0, t0 = 0;
    const frame = (t) => {
      if (!slide.classList.contains("active")) return order.forEach((p) => (p.style.translate = ""));
      if (!home) {
        if (t - slide._fxStart < 2200) return (slide._train = requestAnimationFrame(frame)); // dopo l'ingresso
        const k = 1600 / slide.getBoundingClientRect().width, s = slide.getBoundingClientRect();
        home = order.map((p) => {
          const r = p.getBoundingClientRect();
          return [(r.left - s.left + r.width / 2) * k, (r.top - s.top + r.height / 2) * k];
        });
        const xs = home.map((h) => h[0]), ys = home.map((h) => h[1]);
        const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2;
        // pista: due tratti dritti e due semicerchi ampi (un ovale curva troppo stretto alle estremità
        // e lì le persone si toccherebbero); larga quanto la slide permette
        const rx = Math.max((Math.max(...xs) - Math.min(...xs)) / 2 + 60, Math.min(600, cx - 170, 1430 - cx)), ry = 150, a = rx - ry;
        const pts = [];
        const line = (x0, y0, x1, y1) => { for (let i = 0; i < 60; i++) pts.push([x0 + ((x1 - x0) * i) / 60, y0 + ((y1 - y0) * i) / 60]); };
        const half = (x, a0) => { for (let i = 0; i < 90; i++) pts.push([x + Math.cos(a0 + (i / 90) * Math.PI) * ry, cy + Math.sin(a0 + (i / 90) * Math.PI) * ry]); };
        line(cx - a, cy - ry, cx + a, cy - ry); // sopra, verso destra (parte in alto a sinistra)
        half(cx + a, -Math.PI / 2);
        line(cx + a, cy + ry, cx - a, cy + ry); // sotto, verso sinistra
        half(cx - a, Math.PI / 2);
        pts.push(pts[0]);
        ring = [];
        pts.forEach((pt, i) => ring.push([...pt, i ? ring[i - 1][2] + Math.hypot(pt[0] - pts[i - 1][0], pt[1] - pts[i - 1][1]) : 0]));
        len = ring[ring.length - 1][2];
        t0 = t;
      }
      // partenza morbida: in 3 s scivolano dalle righe alla pista e la velocità sale da zero
      // (lo spostamento è l'integrale di una velocità che cresce con una curva smoothstep)
      const RAMP = 3000, n = order.length, el = t - t0, speed = len / (TRAIN_SLOT_MS * n), u = Math.min(1, el / RAMP);
      const shift = speed * (el < RAMP ? RAMP * (u ** 3 - u ** 4 / 2) : el - RAMP / 2);
      const ease = u * u * (3 - 2 * u);
      const at = (d) => {
        d = ((d % len) + len) % len;
        let lo = 0, hi = ring.length - 1;
        while (hi - lo > 1) ring[(lo + hi) >> 1][2] < d ? (lo = (lo + hi) >> 1) : (hi = (lo + hi) >> 1);
        const a = ring[lo], b = ring[hi], f = (d - a[2]) / (b[2] - a[2] || 1);
        return [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f];
      };
      order.forEach((p, j) => {
        const [x, y] = at((j / n) * len + shift), [hx, hy] = home[j];
        p.style.translate = `${(x - hx) * ease}px ${(y - hy) * ease}px`;
      });
      slide._train = requestAnimationFrame(frame);
    };
    slide._fxStart = performance.now();
    slide._train = requestAnimationFrame(frame);
  }

  const FX_BACK = ["network", "code", "wings"]; // dietro al contenuto
  const FX_MID = ["pizza", "emoji"]; // sotto le scritte, sopra foto, sticker e piè di pagina
  function runFx(slide) {
    slide.querySelectorAll(":scope > canvas.fx").forEach((c) => c.remove());
    slide._spots = [];
    if (STATIC || REDUCED || !slide.dataset.fx) return;
    if (slide.dataset.fx.split(/\s+/).includes("train")) rotatePeople(slide);
    slide.dataset.fx.split(/\s+/).filter((n) => FX[n]).forEach((name) => {
      const cv = document.createElement("canvas");
      cv.className = FX_BACK.includes(name) ? "fx back" : FX_MID.includes(name) ? "fx mid" : "fx";
      cv.width = 1600;
      cv.height = 900;
      if (FX_BACK.includes(name)) slide.prepend(cv);
      else slide.appendChild(cv);
      const ctx = cv.getContext("2d"), step = FX[name](slide), t0 = performance.now();
      let last = t0;
      const frame = (t) => {
        if (!slide.classList.contains("active") || !cv.isConnected) return cv.remove();
        const k = Math.min(3, (t - last) / 16.67); // movimento uguale a 60 e a 120 Hz
        last = t;
        if (name !== "code") ctx.clearRect(0, 0, 1600, 900);
        ctx.globalAlpha = 1;
        if (step(ctx, t - t0, k)) requestAnimationFrame(frame);
        else cv.remove();
      };
      requestAnimationFrame(frame);
    });
  }

  function go(i, fromEnd = false) {
    i = Math.max(0, Math.min(total - 1, i));
    const changed = i !== cur || !slides[i].classList.contains("active");
    cur = i;
    slides.forEach((s, k) => {
      s.classList.toggle("active", k === i);
      s.classList.toggle("before", k < i);
    });
    if (changed) {
      slides[i].querySelectorAll(".map").forEach(drawMap);
      slides[i].querySelectorAll(".road").forEach(drawRoad);
      revealsOf(slides[i]).forEach((r) => r.classList.toggle("shown", fromEnd || STATIC));
      moveBg(i);
      runCounters(slides[i]);
      rollDigits(slides[i]);
      runFx(slides[i]);
    }
    document.getElementById("pn-counter").textContent = `${i + 1} / ${total}`;
    document.getElementById("pn-progress").style.width = `${((i + 1) / total) * 100}%`;
    if (!EMBED) history.replaceState(null, "", `${location.search}#${i + 1}`);
    sync();
  }
  function next() {
    const hidden = revealsOf(slides[cur]).find((r) => !r.classList.contains("shown"));
    if (hidden) {
      hidden.classList.add("shown");
      return sync();
    }
    go(cur + 1);
  }
  function prev() {
    const shown = revealsOf(slides[cur]).filter((r) => r.classList.contains("shown"));
    if (shown.length) {
      shown.at(-1).classList.remove("shown");
      return sync();
    }
    go(cur - 1, true);
  }
  function fit() {
    const sc = Math.min(innerWidth / 1600, innerHeight / 900);
    stage.style.transform = `translate(-50%, -50%) scale(${sc})`;
    if (root.classList.contains("overview")) layoutOverview();
  }
  function toggleFs() {
    document.fullscreenElement ? document.exitFullscreen() : root.requestFullscreen?.();
  }

  // panoramica
  function layoutOverview() {
    const cols = Math.ceil(Math.sqrt(total * 1.6));
    const rows = Math.ceil(total / cols);
    const gap = 40;
    const cellW = (1600 - gap * (cols + 1)) / cols;
    const sc = cellW / 1600;
    const cellH = 900 * sc;
    const gridH = rows * cellH + (rows - 1) * gap;
    const offY = Math.max(gap, (900 - gridH) / 2);
    slides.forEach((s, k) => {
      const c = k % cols, r = Math.floor(k / cols);
      const x = gap + c * (cellW + gap), y = offY + r * (cellH + gap);
      s.style.transformOrigin = "0 0";
      s.style.transform = `translate(${x}px, ${y}px) scale(${sc})`;
    });
  }
  function toggleOverview(force) {
    const on = force ?? !root.classList.contains("overview");
    root.classList.toggle("overview", on);
    if (on) layoutOverview();
    else slides.forEach((s) => (s.style.transform = s.style.transformOrigin = ""));
  }
  stage.addEventListener("click", (e) => {
    if (!root.classList.contains("overview")) return;
    const s = e.target.closest(".slide");
    if (!s) return;
    toggleOverview(false);
    go(slides.indexOf(s));
  });

  // presentatore
  function sync() {
    if (presenterWin && !presenterWin.closed) {
      const s = slides[cur];
      const rv = revealsOf(s);
      presenterWin.postMessage({ pn: "state", cur, total, shown: rv.filter((r) => r.classList.contains("shown")).length, notes: s.querySelector(".notes")?.innerHTML || "" }, "*");
    }
  }
  addEventListener("message", (e) => {
    const d = e.data;
    if (!d || !d.pn) return;
    if (d.pn === "next") next();
    else if (d.pn === "prev") prev();
    else if (d.pn === "go") go(d.cur);
    else if (d.pn === "hello") sync();
  });
  function openPresenter() {
    const url = location.href.split("#")[0].replace(/[?&](static|check)\b/g, "");
    presenterWin = open(url + (url.includes("?") ? "&" : "?") + "presenter", "pn-presenter", "width=1280,height=800");
  }

  addEventListener("keydown", (e) => {
    if (e.target.closest("input, textarea, [contenteditable]")) return;
    const k = e.key;
    if (["ArrowRight", "PageDown", " ", "Enter", "ArrowDown"].includes(k)) {
      e.preventDefault();
      next();
    } else if (["ArrowLeft", "PageUp", "Backspace", "ArrowUp"].includes(k)) {
      e.preventDefault();
      prev();
    } else if (k === "Home") go(0);
    else if (k === "End") go(total - 1);
    else if (k === "f" || k === "F") toggleFs();
    else if (k === "o" || k === "O") toggleOverview();
    else if (k === "Escape" && root.classList.contains("overview")) toggleOverview(false);
    else if (k === "p" || k === "P") {
      // anche Ctrl+P / ⌘P: apre il presentatore al posto della stampa del browser
      e.preventDefault();
      openPresenter();
    } else if ((k === "s" || k === "S") && !e.ctrlKey && !e.metaKey && !e.altKey) printDeck();
  });
  // stampa / PDF: tasto S o pulsante nella barra (Ctrl+P apre il presentatore). Prima porta la
  // pagina allo stato da stampare e aspetta immagini e font (al massimo 4 s), poi apre la stampa.
  let printQueued = false;
  async function printDeck() {
    if (printQueued) return;
    printQueued = true;
    if (root.classList.contains("overview")) toggleOverview(false);
    settleForPrint();
    await Promise.race([preparePrint(), new Promise((r) => setTimeout(r, 4000))]);
    await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
    printQueued = false;
    print();
  }
  document.getElementById("pn-prev").onclick = prev;
  document.getElementById("pn-next").onclick = next;
  document.getElementById("pn-fs").onclick = toggleFs;
  document.getElementById("pn-grid").onclick = () => toggleOverview();
  document.getElementById("pn-print").onclick = printDeck;
  let tx = null;
  addEventListener("touchstart", (e) => (tx = e.touches[0].clientX), { passive: true });
  addEventListener("touchend", (e) => {
    if (tx === null) return;
    const dx = e.changedTouches[0].clientX - tx;
    tx = null;
    if (Math.abs(dx) > 50) dx < 0 ? next() : prev();
  });
  let hideT;
  addEventListener("mousemove", () => {
    document.body.classList.add("show-ui");
    clearTimeout(hideT);
    hideT = setTimeout(() => document.body.classList.remove("show-ui"), 1800);
  });
  addEventListener("resize", fit);
  // #7 apre la slide 7; #fonti la slide che contiene l'elemento con id="fonti"
  const fromHash = () => {
    const h = decodeURIComponent(location.hash.slice(1));
    if (/^\d+$/.test(h)) return +h - 1;
    const i = h ? slides.indexOf(document.getElementById(h)?.closest(".slide")) : -1;
    return i >= 0 ? i : NaN;
  };
  addEventListener("hashchange", () => {
    const i = fromHash();
    if (Number.isFinite(i) && i !== cur) go(i);
  });
  fit();
  const start = fromHash();
  cur = -1;
  go(Number.isFinite(start) ? start : 0);
  if (CHECK) document.fonts.ready.then(() => setTimeout(runCheck, 300));

  /* ---------- ?check: testo fuori dai bordi, sovrapposizioni, font troppo piccoli ---------- */
  function runCheck() {
    const report = [];
    const MIN_FONT = 17;
    slides.forEach((s, idx) => {
      s.classList.add("active");
      const issues = [];
      const sr = s.getBoundingClientRect();
      const scale = sr.width / 1600;
      const px = (v) => Math.round(v / scale);
      const foot = s.querySelector(".slide-foot");
      const footTop = foot ? foot.getBoundingClientRect().top : sr.bottom;
      const els = [...s.querySelectorAll("*")].filter((el) => !el.closest(".notes, .slide-foot, .slide-num, .crumb, .orbit, .bg, svg") && !el.matches(".sticker, .w, br"));
      for (const el of els) {
        const r = el.getBoundingClientRect();
        if (!r.width && !r.height) continue;
        const name = describe(el);
        const decor = el.matches(".n, .stamp, .cloud > span, .cloud > span *") || el.closest(".section > .n");
        if (!decor && (r.left < sr.left - 1 || r.right > sr.right + 1 || r.top < sr.top - 1 || r.bottom > sr.bottom + 1)) {
          issues.push(`esce dalla slide: ${name} (${px(r.right - sr.right)}px a destra, ${px(r.bottom - sr.bottom)}px sotto)`);
          el.setAttribute("data-overflow", "");
        } else if (!decor && foot && el.closest(".body") && r.bottom > footTop + 2 && el.children.length === 0) {
          issues.push(`copre il footer: ${name}`);
          el.setAttribute("data-overflow", "");
        }
        const cs = getComputedStyle(el);
        if ((el.scrollHeight > el.clientHeight + 2 && /hidden|clip|auto/.test(cs.overflowY) && !el.matches(".bars > .bar > i, .ph, .window > .scroll")) || (el.scrollWidth > el.clientWidth + 2 && /hidden|clip|auto/.test(cs.overflowX) && !el.matches(".ph"))) {
          issues.push(`contenuto tagliato dentro: ${name}`);
          el.setAttribute("data-overflow", "");
        }
        const glass = el.parentElement?.closest(".glass, .cards > *, .stats > *, .teams > *, .timeline > li, .agenda > li, .irows > li > p");
        if (glass && el.children.length === 0) {
          const g = glass.getBoundingClientRect();
          if (r.right > g.right + 2 || r.bottom > g.bottom + 2) {
            issues.push(`testo fuori dalla card: ${name}`);
            el.setAttribute("data-overflow", "");
          } else if (cs.display !== "inline" && el.clientWidth > 0 && el.scrollWidth > el.clientWidth + 2) {
            // una parola che non va a capo (un dominio, un nome lungo) esce dal suo riquadro anche se il riquadro sta nella card
            issues.push(`testo più largo della card: ${name}`);
            el.setAttribute("data-overflow", "");
          }
        }
        const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
        if (own && parseFloat(cs.fontSize) < MIN_FONT && !el.closest(".ph, .qr figcaption")) issues.push(`testo troppo piccolo (${cs.fontSize}): ${name}`);
      }
      // contenuto troppo alto: centrato in verticale, risale sopra titolo e sottotitolo.
      // Conta solo dove si sovrappone davvero al testo (un telefono alto a destra non copre il titolo a sinistra).
      const body = s.querySelector(":scope > .body");
      const headText = [...s.querySelectorAll(":scope > h1, :scope > .kicker, :scope > .sub")].map((h) => {
        const range = document.createRange();
        range.selectNodeContents(h);
        return range.getBoundingClientRect();
      });
      if (body && headText.length) {
        const boxes = [...body.querySelectorAll("*")].filter(
          (el) => !el.closest(".crumb") && (el.children.length === 0 || el.matches("img, .phone, .qr")) && !el.matches("br, .w") && !el.closest("svg")
        );
        let worst = 0;
        for (const el of boxes) {
          const r = el.getBoundingClientRect();
          if (!r.width || !r.height) continue;
          for (const h of headText) {
            const dx = Math.min(r.right, h.right) - Math.max(r.left, h.left);
            const dy = Math.min(r.bottom, h.bottom) - Math.max(r.top, h.top);
            if (dx > 2 && dy > 2) worst = Math.max(worst, dy);
          }
        }
        if (worst) issues.push(`il contenuto copre il titolo (${px(worst)}px): accorcia, dividi la slide o usa un componente più compatto`);
      }
      const ag = s.querySelector(".agenda");
      if (READ && ag && ag.children.length > sections.length) issues.push(`indice con ${ag.children.length} voci ma ${sections.length} sezioni: serve una slide con data-section per voce, altrimenti l'indice non è cliccabile`);
      if (!READ && s.querySelector(".body > p.small")) issues.push("riga piccola (p.small): da lontano non si legge, toglila e mettila nelle note");
      s.querySelectorAll(".ref-missing").forEach((el) => issues.push(`rimando a una slide che non c'è: data-ref="${el.dataset.ref}" (manca id="${el.dataset.ref}")`));
      s.querySelectorAll(".map .node[data-to]").forEach((n) => {
        const ids = new Set([...n.closest(".map").querySelectorAll(".node[data-id]")].map((x) => x.dataset.id));
        n.dataset.to.split(/\s+/).filter((id) => id && !ids.has(id)).forEach((id) => issues.push(`mappa: data-to="${id}" non corrisponde a nessun data-id`));
      });
      if (s.querySelector(".ph")) issues.push(`immagini mancanti: ${[...s.querySelectorAll(".ph span:last-child")].map((x) => x.textContent).join(", ")}`);
      const todos = [...s.querySelectorAll(".todo")].map((x) => x.textContent.trim());
      if (todos.length) issues.push(`dati da completare (.todo): ${todos.join(" · ")}`);
      s.classList.toggle("active", idx === cur);
      if (issues.length) report.push({ slide: idx + 1, title: [...(s.querySelector("h1")?.childNodes || [])].filter((n) => !n.classList?.contains("n")).map((n) => n.textContent).join("").trim().slice(0, 60), issues: [...new Set(issues)] });
    });
    const json = JSON.stringify({ slides: total, ok: report.length === 0, report }, null, 1);
    const out = document.createElement("script");
    out.type = "application/json";
    out.id = "pn-check";
    out.textContent = json;
    document.body.appendChild(out);
    const box = document.createElement("pre");
    box.id = "pn-check-report";
    box.textContent = report.length ? json : `OK: ${total} slide, nessun problema`;
    document.body.appendChild(box);
    console.log("PN_CHECK " + json);
  }
  function describe(el) {
    const t = (el.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40);
    const c = el.className && typeof el.className === "string" ? "." + el.className.trim().split(/\s+/).join(".") : "";
    return `<${el.tagName.toLowerCase()}${c}>${t ? ` "${t}"` : ""}`;
  }

  /* ---------- Vista presentatore ---------- */
  function presenterView() {
    root.classList.add("presenter");
    const base = location.href.split("#")[0].replace(/[?&]presenter\b/, "");
    const emb = base + (base.includes("?") ? "&" : "?") + "embed";
    document.body.insertAdjacentHTML(
      "beforeend",
      `<div class="pv">
        <div class="pv-bar"><span id="pv-count">–</span><span class="pv-time" id="pv-time">00:00</span><span>← → · P</span></div>
        <div><h4>${T.now}</h4><iframe id="pv-cur" src="${emb}#1"></iframe></div>
        <div class="pv-next"><h4>${T.next2}</h4><iframe id="pv-next" src="${emb}#2"></iframe></div>
        <div class="pv-notes"><h4>${T.notes}</h4><div id="pv-notes"></div></div>
      </div>`,
    );
    const t0 = Date.now();
    setInterval(() => {
      const s = Math.floor((Date.now() - t0) / 1000);
      document.getElementById("pv-time").textContent = `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
    }, 1000);
    const send = (m) => opener && opener.postMessage({ pn: m }, "*");
    addEventListener("message", (e) => {
      const d = e.data;
      if (!d || d.pn !== "state") return;
      document.getElementById("pv-count").textContent = `${d.cur + 1} / ${d.total}`;
      document.getElementById("pv-notes").innerHTML = d.notes || `<p>${T.nonotes}</p>`;
      document.getElementById("pv-cur").src = `${emb}#${d.cur + 1}`;
      document.getElementById("pv-next").src = d.cur + 1 < d.total ? `${emb}#${d.cur + 2}` : "about:blank";
    });
    addEventListener("keydown", (e) => {
      if (["ArrowRight", "PageDown", " ", "Enter", "ArrowDown"].includes(e.key)) (e.preventDefault(), send("next"));
      else if (["ArrowLeft", "PageUp", "Backspace", "ArrowUp"].includes(e.key)) (e.preventDefault(), send("prev"));
    });
    send("hello");
  }
})();
