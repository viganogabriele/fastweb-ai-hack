/* Scene-specific motion. Only the visible scene owns an animation frame. */
(() => {
  const root = document.documentElement;
  const stage = document.getElementById("stage");
  const preference = matchMedia("(prefers-reduced-motion: reduce)");
  const svgNS = "http://www.w3.org/2000/svg";
  const signals = [
    ["EMAIL / NEGOZIO", "Taglia M esaurita", "Richieste non soddisfatte", true],
    ["CATALOGO", "Modello, colore, taglia", "Collegamento al prodotto", false],
    ["REPORT", "I numeri disponibili", "Baseline e contesto", false],
    ["VERIFICA", "Stock da controllare", "Disponibilità, riserve, tempi", true],
    ["EMAIL / MIL01", "Cardigan logo in M", "Nero e blu", true],
    ["PLANNING", "Una proposta da valutare", "La decisione resta umana", false],
  ];

  document.querySelectorAll("[data-mail-wall]").forEach((wall) => {
    [0, 3, 1].forEach((offset, index) => {
      const column = document.createElement("div");
      column.className = "mail-column";
      const track = document.createElement("div");
      track.className = "mail-track";
      track.style.setProperty("--stream-time", `${[65, 80, 72][index]}s`);
      const sequence = [...signals.slice(offset), ...signals.slice(0, offset)];
      [...sequence, ...sequence].forEach(([source, title, detail, hot]) => {
        const card = document.createElement("div");
        card.className = `mail-card${hot ? " hot" : ""}`;
        const top = document.createElement("div");
        top.className = "mail-card-top";
        const label = document.createElement("span");
        label.textContent = source;
        const icon = document.createElement("span");
        icon.textContent = "↗";
        top.append(label, icon);
        const heading = document.createElement("strong");
        heading.textContent = title;
        const caption = document.createElement("small");
        caption.textContent = detail;
        card.append(top, heading, caption);
        track.append(card);
      });
      column.append(track);
      wall.append(column);
    });
  });

  const flows = new Map();
  document.querySelectorAll(".scene").forEach((scene) => {
    const paths = [...scene.querySelectorAll("[data-packet-path]")];
    const packets = paths.flatMap((path, pathIndex) => {
      const layer = path.closest("svg").querySelector("[data-particles]");
      if (!layer) return [];
      const length = path.getTotalLength();
      const samples = Array.from({ length: 65 }, (_, i) => path.getPointAtLength(length * i / 64));
      return Array.from({ length: 4 }, (_, i) => {
        const dot = document.createElementNS(svgNS, "circle");
        dot.setAttribute("r", "5");
        dot.setAttribute("fill", scene.classList.contains("light") ? "#9b1b30" : path.dataset.packetPath === "incoming" ? "#f5f4f1" : "#f08a9b");
        layer.append(dot);
        return { dot, samples, length, phase: (i / 4 + pathIndex * .13) % 1 };
      });
    });
    if (packets.length) flows.set(scene, packets);
  });

  let frame = 0;
  let current = null;
  let start = 0;
  let last = 0;
  let highlighted = -1;

  function draw(now) {
    if (!current) return;
    if (now - last >= 30) {
      last = now;
      const elapsed = Math.max(0, (now - start) / 1000);
      for (const packet of flows.get(current) || []) {
        const progress = (packet.phase + elapsed * 85 / packet.length) % 1;
        const position = progress * 64;
        const index = Math.min(63, Math.floor(position));
        const fraction = position - index;
        const a = packet.samples[index], b = packet.samples[index + 1];
        packet.dot.setAttribute("cx", a.x + (b.x - a.x) * fraction);
        packet.dot.setAttribute("cy", a.y + (b.y - a.y) * fraction);
        packet.dot.setAttribute("opacity", Math.min(1, progress * 10, (1 - progress) * 10));
      }
      const tools = current.querySelectorAll(".tool-node");
      const selected = Math.floor(elapsed / 1.8) % 3;
      if (tools.length && selected !== highlighted) {
        highlighted = selected;
        tools.forEach((node, index) => node.classList.toggle("tool-lit", index === selected));
      }
    }
    frame = requestAnimationFrame(draw);
  }

  function refresh() {
    cancelAnimationFrame(frame);
    const next = stage.querySelector(".scene.active");
    if (next !== current) {
      current?.querySelectorAll(".tool-lit").forEach((node) => node.classList.remove("tool-lit"));
      current = next;
      start = performance.now();
      highlighted = -1;
    }
    const paused = preference.matches || root.classList.contains("static") || root.classList.contains("overview") || document.hidden;
    if (paused || !current) return;
    if (flows.has(current)) frame = requestAnimationFrame(draw);
  }

  new MutationObserver((records) => {
    if (records.some((record) => record.target.classList.contains("scene"))) refresh();
  }).observe(stage, { attributes: true, attributeFilter: ["class"], subtree: true });
  new MutationObserver(refresh).observe(root, { attributes: true, attributeFilter: ["class"] });
  preference.addEventListener("change", refresh);
  document.addEventListener("visibilitychange", refresh);

  const motionButton = document.createElement("button");
  motionButton.id = "tesseract-motion";
  motionButton.type = "button";
  motionButton.title = "Pausa / riprendi animazioni (M)";
  motionButton.setAttribute("aria-label", "Pausa / riprendi animazioni");
  motionButton.setAttribute("aria-pressed", "false");
  motionButton.innerHTML = '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 5v14M16 5v14"/></svg>';
  const toggleMotion = () => {
    root.classList.toggle("static");
    motionButton.setAttribute("aria-pressed", String(root.classList.contains("static")));
  };
  motionButton.addEventListener("click", toggleMotion);
  document.querySelector(".ui")?.append(motionButton);
  addEventListener("keydown", (event) => {
    if (event.key.toLowerCase() !== "m" || event.ctrlKey || event.metaKey || event.altKey || event.target.closest("input, textarea, [contenteditable]")) return;
    event.preventDefault();
    toggleMotion();
  });
  refresh();
})();
