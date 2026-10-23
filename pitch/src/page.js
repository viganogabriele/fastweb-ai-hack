// Adds running header and page numbers, then flags pages whose content overflows.
// build.py reads the result from <body data-overflow="...">.
document.fonts.ready.then(() => {
  const doc = document.body.dataset.doc || "";
  const it = document.documentElement.lang === "it";
  const pack = it ? "kit del pitch" : "pitch pack";
  const disclaimer = it ? "Dati sintetici · Valentino è un brand dimostrativo" : "Synthetic data · Valentino is demo branding";
  const pages = [...document.querySelectorAll(".page")];
  pages.forEach((page, i) => {
    if (!page.classList.contains("cover")) {
      page.insertAdjacentHTML(
        "afterbegin",
        `<div class="running"><span><b>Tessera</b> · ${pack}</span><span>${doc}</span></div>`,
      );
      page.insertAdjacentHTML(
        "beforeend",
        `<div class="folio"><span>${disclaimer}</span><span>${i + 1} / ${pages.length}</span></div>`,
      );
    }
  });
  const overflowing = pages
    .map((page, i) => {
      const limit = page.getBoundingClientRect().bottom - 14 * 3.7795; // keep 14mm clear for the folio
      const deepest = Math.max(
        ...[...page.querySelectorAll(".body *, .cover *")].map((el) => el.getBoundingClientRect().bottom),
      );
      return deepest > limit ? i + 1 : null;
    })
    .filter((n) => n !== null);
  overflowing.forEach((n) => pages[n - 1].setAttribute("data-overflow", ""));
  document.body.dataset.overflow = overflowing.join(",");
  document.body.dataset.ready = "1";
});
