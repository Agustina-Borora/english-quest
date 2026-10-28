// Mini tutorial guiado: oscurece la pantalla, resalta cada parte y explica para qué sirve.
// Cada pantalla define window.TOUR = { key: "...", steps: [{ el: "selector", title: "...", text: "..." }] }
// La primera vez arranca solo; después se puede abrir con cualquier elemento que tenga data-tour-start.
(function () {
  function startTour(tour) {
    const steps = tour.steps;
    let i = 0;
    const shade = document.createElement("div"); shade.className = "tour-shade";
    const hole = document.createElement("div"); hole.className = "tour-hole";
    const box = document.createElement("div"); box.className = "tour-box";
    document.body.append(shade, hole, box);

    function target() {
      const el = steps[i].el ? document.querySelector(steps[i].el) : null;
      return el && el.getBoundingClientRect().width > 0 ? el : null;
    }

    function place() {
      const el = target();
      if (el) {
        const r = el.getBoundingClientRect(), pad = 8;
        hole.style.cssText = `display:block;top:${r.top - pad}px;left:${r.left - pad}px;` +
                             `width:${r.width + pad * 2}px;height:${r.height + pad * 2}px`;
        shade.classList.remove("dark");
        box.className = "tour-box " + (r.top + r.height / 2 < innerHeight / 2 ? "at-bottom" : "at-top");
      } else {
        hole.style.display = "none";
        shade.classList.add("dark");
        box.className = "tour-box at-center";
      }
    }

    function show() {
      const s = steps[i], last = i === steps.length - 1;
      box.innerHTML =
        `<div class="tour-count">${i + 1} / ${steps.length}</div>` +
        `<h3>${s.title}</h3><p>${s.text}</p>` +
        `<div class="tour-btns">` +
        (last ? "" : `<button type="button" class="tour-skip">Saltar</button>`) +
        (i > 0 ? `<button type="button" class="btn light tour-prev">⬅</button>` : "") +
        `<button type="button" class="btn tour-next">${last ? "¡Listo! 🎉" : "Siguiente ➡"}</button></div>`;
      box.querySelector(".tour-next").onclick = () => (last ? end() : (i++, show()));
      const prev = box.querySelector(".tour-prev"); if (prev) prev.onclick = () => { i--; show(); };
      const skip = box.querySelector(".tour-skip"); if (skip) skip.onclick = end;
      const el = target();
      if (el) el.scrollIntoView({ block: "center" });
      place();
    }

    function end() {
      shade.remove(); hole.remove(); box.remove();
      removeEventListener("resize", place); removeEventListener("scroll", place);
      try { localStorage.setItem("tour_" + tour.key, "1"); } catch (e) { /* sin almacenamiento */ }
      if (tour.onEnd) tour.onEnd();
    }

    addEventListener("resize", place); addEventListener("scroll", place);
    show();
  }

  window.tourSeen = key => {
    try { return localStorage.getItem("tour_" + key) === "1"; } catch (e) { return true; }
  };

  document.addEventListener("DOMContentLoaded", () => {
    const tour = window.TOUR;
    if (!tour) return;
    document.querySelectorAll("[data-tour-start]").forEach(b => b.addEventListener("click", e => {
      e.preventDefault(); startTour(tour);
    }));
    if (!window.tourSeen(tour.key)) setTimeout(() => startTour(tour), 600);
  });
})();
