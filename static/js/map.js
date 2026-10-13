// Mapa de la aventura: cada lección es un lugar; la personita camina hasta él
(function () {
  const map = $("#map");
  if (!map || !window.LESSONS.length) return;
  const L = window.LESSONS;
  const W = 1000, ROW = 250, TOP = 260;
  const H = TOP + L.length * ROW + 80;
  map.style.aspectRatio = `${W} / ${H}`;

  const start = { x: 500, y: 80 };
  const pts = L.map((_, i) => ({ x: i % 2 === 0 ? 270 : 730, y: TOP + 80 + i * ROW }));

  // Camino curvo que une todos los lugares
  let d = `M${start.x} ${start.y}`;
  let prev = start;
  pts.forEach(p => {
    const my = (prev.y + p.y) / 2;
    d += ` C${prev.x} ${my}, ${p.x} ${my}, ${p.x} ${p.y}`;
    prev = p;
  });

  // Decoración: árboles, flores y un laguito
  const tree = (x, y, s) => `<g transform="translate(${x} ${y}) scale(${s})"><rect x="-6" y="0" width="12" height="34" rx="4" fill="#8a5a3b"/>
    <circle cx="0" cy="-12" r="30" fill="#2f9e44"/><circle cx="-18" cy="4" r="20" fill="#37b24d"/><circle cx="18" cy="2" r="22" fill="#37b24d"/></g>`;
  const flower = (x, y, c) => `<g transform="translate(${x} ${y})"><circle r="7" fill="${c}"/><circle r="3" fill="#ffd23f"/></g>`;
  let deco = "";
  pts.forEach((p, i) => {
    const side = i % 2 === 0 ? 1 : -1;
    deco += tree(p.x + side * 330 + (i % 3) * 10, p.y - 40, 1.1);
    deco += tree(p.x + side * 400, p.y + 70, .8);
    deco += flower(p.x - side * 160, p.y + 110, ["#ff5fa2", "#fff", "#9b5de5"][i % 3]);
    deco += flower(p.x - side * 130, p.y + 128, "#ffd23f");
    if (i % 3 === 1) deco += `<ellipse cx="${p.x + side * 280}" cy="${p.y + 150}" rx="90" ry="34" fill="#5bc0eb" stroke="#fff" stroke-width="6"/>`;
  });

  map.innerHTML = `
    <svg class="ground" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
      <defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fdc6e"/><stop offset="1" stop-color="#5fbf4a"/></linearGradient></defs>
      <rect width="${W}" height="${H}" fill="url(#g)"/>
      ${Array.from({ length: 40 }, (_, i) => `<ellipse cx="${(i * 197) % W}" cy="${(i * 331) % H}" rx="40" ry="10" fill="#fff" opacity=".07"/>`).join("")}
      ${deco}
      <path d="${d}" fill="none" stroke="#c99a5b" stroke-width="64" stroke-linecap="round"/>
      <path d="${d}" fill="none" stroke="#f4dfb0" stroke-width="52" stroke-linecap="round"/>
      <path d="${d}" fill="none" stroke="#fff" stroke-width="5" stroke-dasharray="16 18" stroke-linecap="round"/>
    </svg>
    <span class="start-flag" style="left:${start.x / W * 100}%;top:${start.y / H * 100}%">🏁 Start</span>
    ${L.map((l, i) => `
      <button class="spot ${l.done === l.acts ? "done" : ""}" data-i="${i}" style="left:${pts[i].x / W * 100}%;top:${pts[i].y / H * 100}%">
        <span class="num">${i + 1}</span>
        <span class="stars">${l.done === l.acts ? "✔ " : ""}⭐ ${l.done}/${l.acts}</span>
        <div class="bld">${buildingSVG(l.scene)}</div>
        <span class="tag">${esc(l.title)}<small>${esc(SCENE_INFO[l.scene] ? SCENE_INFO[l.scene].es : "")}</small></span>
      </button>`).join("")}
    <div class="walker" id="walker"><span class="bubble">¡Hola, ${esc(window.FIRST_NAME)}!</span>${avatarSVG(window.ME)}</div>`;

  // La personita aparece en el último lugar que visitó
  let lastId = null;
  try { lastId = +localStorage.getItem("eq_last_lesson"); } catch (e) {}
  const lastIdx = L.findIndex(l => l.id === lastId);
  const placeWalker = p => {
    const w = $("#walker");
    w.style.left = (p.x + (p === start ? 150 : 95)) / W * 100 + "%";
    w.style.top = (p.y + (p === start ? 250 : 60)) / H * 100 + "%";
  };
  placeWalker(lastIdx >= 0 ? pts[lastIdx] : start);

  $$("#map .spot").forEach(b => b.onclick = () => {
    const i = +b.dataset.i;
    const w = $("#walker");
    $(".bubble", w).textContent = "Let's go! 🚶";
    w.classList.add("walking");
    placeWalker(pts[i]);
    speak("Let's go!");
    try { localStorage.setItem("eq_last_lesson", L[i].id); } catch (e) {}
    setTimeout(() => { location.href = window.LESSON_URL + L[i].id; }, 1050);
  });
})();
