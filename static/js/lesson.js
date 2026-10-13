// Lección: actividades en el orden que eligió la profe
const LS = window.LESSON;
const WORDS = LS.words;
let progress = LS.progress || {};
let current = 0;
let cleanup = null;   // para sacar eventos de teclado al cambiar de actividad

$("#lesson-building").innerHTML = buildingSVG(LS.scene);

function stepper() {
  $("#stepper").innerHTML = LS.activities.map((a, i) => {
    const ok = progress[a] && progress[a].passed;
    return `<button class="${i === current ? "now" : ""}" data-i="${i}"><span class="st">${ok ? "⭐" : "☆"}</span>${ACTS[a].emoji} ${ACTS[a].name}</button>`;
  }).join("");
  $$("#stepper button").forEach(b => b.onclick = () => openActivity(+b.dataset.i));
}

function openActivity(i) {
  if (cleanup) { cleanup(); cleanup = null; }
  current = i;
  stepper();
  $("#below").innerHTML = "";
  if (!WORDS.length) {
    $("#stage").innerHTML = `<div class="challenge"><div class="prompt"><span class="p-emoji">📭</span><p class="p-label">Esta lección todavía no tiene palabras.</p></div></div>`;
    return;
  }
  const a = LS.activities[i];
  ({ explore, cards, read, write, quiz })[a]();
}

// ------------------------------------------------------------ resultado y guardado
async function finish(activity, score, total) {
  const needed = (activity === "explore" || activity === "cards") ? total : Math.ceil(total * 0.6);
  let passed = score >= needed, coinsWon = score * 5, firstPass = passed && !(progress[activity] && progress[activity].passed);
  if (!window.PREVIEW) {
    try {
      const r = await postJSON(window.SAVE_URL, { lesson_id: LS.id, activity, score, total });
      passed = r.passed; coinsWon = r.coins_won; firstPass = r.first_pass; progress = r.progress;
      $("#coins").textContent = `🪙 ${r.coins}`;
    } catch (e) { toast("No se pudo guardar 😕"); }
  } else if (passed) {
    progress[activity] = { passed: true, best: score, total };
  }
  stepper();
  const isLast = current >= LS.activities.length - 1;
  const allDone = LS.activities.every(a => progress[a] && progress[a].passed);
  const scoreLine = (activity === "explore" || activity === "cards") ? "" :
    `<p style="font-size:1.2rem">Acertaste <b>${score}</b> de <b>${total}</b>${passed ? "" : ` · necesitás ${needed}`}</p>`;
  modal(`
    <div class="mini-av">${avatarSVG(window.ME)}</div>
    <div class="result-stars">${passed ? "⭐" : "☆"}</div>
    <h2>${allDone && firstPass ? "🏆 ¡Completaste la lección!" : passed ? (firstPass ? "¡Ganaste una estrella!" : "¡Muy bien otra vez! 👏") : "¡Casi! Probá otra vez 💪"}</h2>
    ${scoreLine}
    <p style="font-size:1.2rem">🪙 +${coinsWon} monedas</p>
    <div class="row">
      ${passed ? "" : `<button class="btn yellow" data-a="retry">🔄 Reintentar</button>`}
      ${!isLast ? `<button class="btn green" data-a="next">Siguiente: ${ACTS[LS.activities[current + 1]].emoji} ${ACTS[LS.activities[current + 1]].name} ➜</button>` : ""}
      <a class="btn ${isLast ? "green" : "light"}" href="${window.MAP_URL}">🗺️ Volver al mapa</a>
    </div>`, box => {
    const r = $("[data-a=retry]", box); if (r) r.onclick = () => { closeModal(); openActivity(current); };
    const n = $("[data-a=next]", box); if (n) n.onclick = () => { closeModal(); openActivity(current + 1); };
  });
  if (passed) { beep("win"); confetti(allDone && firstPass ? 180 : 70); speak(allDone ? "Amazing! You finished the lesson!" : "Great job!"); }
  else speak("Almost! Try again!");
}

function modal(html, bind) {
  closeModal();
  const back = document.createElement("div");
  back.className = "modal-back"; back.id = "modal";
  back.innerHTML = `<div class="modal">${html}</div>`;
  document.body.appendChild(back);
  if (bind) bind(back);
}
function closeModal() { const m = $("#modal"); if (m) m.remove(); }

function dots(el, n, results, now) {
  el.innerHTML = Array.from({ length: n }, (_, i) =>
    `<span class="${results[i] === true ? "ok" : results[i] === false ? "no" : i === now ? "now" : ""}"></span>`).join("");
}
function others(w, n, pool = WORDS) { return shuffle(pool.filter(x => x !== w)).slice(0, n); }

// ------------------------------------------------------------ 1) Explorar
function explore() {
  const PAGE = SCENE_SLOTS.length;
  const pages = Math.ceil(WORDS.length / PAGE);
  const seen = new Set();
  let page = 0;
  const draw = () => {
    const items = WORDS.slice(page * PAGE, page * PAGE + PAGE);
    $("#stage").innerHTML = `<div class="scene">${sceneSVG(LS.scene)}
      ${items.map((w, i) => `<button class="obj ${seen.has(w.word) ? "seen" : ""}" data-w="${page * PAGE + i}" style="left:${SCENE_SLOTS[i][0]}%;top:${SCENE_SLOTS[i][1]}%;animation-delay:${-i * .4}s">${w.emoji || "⭐"}</button>`).join("")}
      <div class="guide">${avatarSVG(window.ME)}</div>
      <div class="say-bubble">Tap everything! 👆 <small>Tocá todo</small></div></div>`;
    $("#below").innerHTML = `<div class="bar-row"><span>🔍 Descubiertas: ${seen.size}/${WORDS.length}</span>
      <div class="progress"><div style="width:${seen.size / WORDS.length * 100}%"></div></div>
      ${pages > 1 ? `<button class="btn small ghost" id="pg">${page + 1}/${pages} ➜ Más cosas</button>` : ""}</div>`;
    const pg = $("#pg"); if (pg) pg.onclick = () => { page = (page + 1) % pages; draw(); };
    $$("#stage .obj").forEach(b => b.onclick = () => {
      const w = WORDS[+b.dataset.w];
      const isNew = !seen.has(w.word);
      seen.add(w.word);
      speak(w.word);
      modal(`
        <span class="w-emoji">${w.emoji || "⭐"}</span>
        <div class="w-word">${esc(w.word)}</div>
        <div class="w-es">🇦🇷 ${esc(w.translation)}</div>
        ${w.sentence ? `<div class="w-sentence"><button class="say" data-s>🔊</button><span>${esc(w.sentence)}</span></div>` : ""}
        <div class="row"><button class="btn yellow" data-again>🔊 Otra vez</button><button class="btn green" data-ok>¡Entendido! ✔</button></div>`, box => {
        const s = $("[data-s]", box); if (s) s.onclick = () => speak(w.sentence);
        $("[data-again]", box).onclick = () => speak(w.word, .7);
        $("[data-ok]", box).onclick = () => {
          closeModal(); draw();
          if (isNew && seen.size === WORDS.length) finish("explore", WORDS.length, WORDS.length);
        };
      });
    });
  };
  draw();
}

// ------------------------------------------------------------ 2) Tarjetas
function cards() {
  const viewed = new Set();
  let i = 0;
  const draw = () => {
    const w = WORDS[i];
    $("#stage").innerHTML = `<div class="flip-area">${sceneSVG(LS.scene)}
      <div class="flip" id="flip"><div class="in">
        <div class="face front"><span class="big-e">${w.emoji || "⭐"}</span><div class="w">${esc(w.word)}</div><div class="hint">👆 Tocá para dar vuelta</div></div>
        <div class="face back"><div class="w">${esc(w.translation)}</div>${w.sentence ? `<div class="s">${esc(w.sentence)}</div>` : ""}<div class="hint" style="color:#fff">👆 Tocá para volver</div></div>
      </div></div>
      <div class="flip-nav">
        <button class="btn white" id="prev" ${i === 0 ? "disabled" : ""}>⬅</button>
        <button class="say" id="say">🔊</button>
        <b style="color:var(--ink);background:#fff;border-radius:99px;padding:6px 14px">${i + 1} / ${WORDS.length}</b>
        <button class="btn white" id="next">${i === WORDS.length - 1 ? "🏁" : "➡"}</button>
      </div></div>`;
    speak(w.word);
    $("#flip").onclick = () => { $("#flip").classList.toggle("flipped"); viewed.add(i); bar(); if (!$("#flip").classList.contains("flipped")) speak(w.word); };
    $("#say").onclick = () => speak(w.word, .7);
    $("#prev").onclick = () => { i--; draw(); };
    $("#next").onclick = () => {
      viewed.add(i);
      if (i < WORDS.length - 1) { i++; draw(); }
      else finish("cards", viewed.size, WORDS.length);
    };
    bar();
  };
  const bar = () => {
    $("#below").innerHTML = `<div class="bar-row"><span>🃏 Tarjetas vistas: ${viewed.size}/${WORDS.length}</span><div class="progress"><div style="width:${viewed.size / WORDS.length * 100}%"></div></div></div>`;
  };
  draw();
}

// ------------------------------------------------------------ 3) Leer y escuchar
function read() {
  const order = shuffle(WORDS).slice(0, Math.min(6, WORDS.length));
  const results = [];
  let round = 0;
  $("#stage").innerHTML = `<div class="challenge"><div class="dots" id="d"></div><div class="prompt" id="p"></div><div class="opt-grid" id="o"></div></div>`;
  const next = () => {
    if (round >= order.length) return finish("read", results.filter(Boolean).length, order.length);
    dots($("#d"), order.length, results, round);
    const t = order[round];
    const opts = shuffle([t, ...others(t, Math.min(3, WORDS.length - 1))]);
    const listen = round % 2 === 1;
    if (listen) {
      $("#p").innerHTML = `<p class="p-label">👂 Escuchá y tocá la palabra correcta</p><button class="listen-btn" id="lb">🔊</button>`;
      $("#lb").onclick = () => speak(t.word, .75);
      setTimeout(() => speak(t.word, .75), 300);
      $("#o").innerHTML = opts.map((o, i) => `<button class="opt" data-i="${i}">${esc(o.word)}</button>`).join("");
    } else {
      $("#p").innerHTML = `<p class="p-label">📖 Leé la palabra y tocá el dibujo</p><div class="p-word">${esc(t.word)}</div>`;
      $("#o").innerHTML = opts.map((o, i) => `<button class="opt emoji" data-i="${i}">${o.emoji || esc(o.translation)}</button>`).join("");
    }
    let locked = false;
    $$("#o .opt").forEach(b => b.onclick = () => {
      if (locked) return; locked = true;
      const ok = opts[+b.dataset.i] === t;
      results[round] = ok;
      b.classList.add(ok ? "ok" : "no");
      if (!ok) $$("#o .opt")[opts.indexOf(t)].classList.add("ok");
      beep(ok ? "good" : "bad");
      setTimeout(() => speak(t.word), 250);
      round++; dots($("#d"), order.length, results, round);
      setTimeout(next, 1400);
    });
  };
  next();
}

// ------------------------------------------------------------ 4) Escribir
function write() {
  const order = shuffle(WORDS).slice(0, Math.min(5, WORDS.length));
  const results = [];
  let round = 0, typed = [], tiles = [], tries = 0, busy = false, letters = [];
  $("#stage").innerHTML = `<div class="challenge"><div class="dots" id="d"></div>
    <div class="prompt"><span class="p-emoji" id="we"></span><p class="p-label">¿Cómo se escribe <b id="wes"></b> en inglés?</p><button class="say" id="ws">🔊</button></div>
    <div class="slots" id="sl"></div><div class="tiles" id="tl"></div><p class="reveal-msg" id="rv"></p>
    <div style="text-align:center;margin-top:6px"><button class="btn small purple" id="clr">↩ Borrar</button></div></div>`;

  const word = () => order[round].word.toLowerCase();
  const render = () => {
    const w = word();
    let k = 0;
    $("#sl").className = "slots";
    $("#sl").innerHTML = [...w].map(ch => {
      if (!/[a-z]/.test(ch)) return `<span class="slot space">${ch === " " ? "" : esc(ch)}</span>`;
      const pos = k++, t = typed[pos];
      return `<span class="slot ${t !== undefined ? "filled" : ""}" data-p="${pos}">${t !== undefined ? tiles[t] : ""}</span>`;
    }).join("");
    $("#tl").innerHTML = tiles.map((l, i) => `<button class="tile-l ${typed.includes(i) ? "used" : ""}" data-i="${i}">${l}</button>`).join("");
    $$("#tl .tile-l").forEach(b => b.onclick = () => add(+b.dataset.i));
    $$("#sl .slot[data-p]").forEach(s => s.onclick = () => removeFrom(+s.dataset.p));
  };
  const add = i => {
    if (busy || typed.includes(i) || typed.length >= letters.length) return;
    typed.push(i); render();
    if (typed.length === letters.length) check();
  };
  const removeFrom = p => { if (busy || p >= typed.length) return; typed = typed.slice(0, p); render(); };
  const check = () => {
    busy = true;
    const ok = typed.map(i => tiles[i]).join("") === letters.join("");
    const t = order[round];
    if (ok) {
      $("#sl").classList.add("ok"); results[round] = tries === 0; beep("good"); speak(t.word);
      $("#rv").textContent = tries === 0 ? "🎉 Perfect!" : "👍 ¡Bien!";
      setTimeout(() => { round++; nextRound(); }, 1400);
    } else {
      tries++; $("#sl").classList.add("no"); beep("bad");
      if (tries >= 2) {
        results[round] = false;
        $("#rv").innerHTML = `Se escribe: <b style="color:var(--purple);font-size:1.5rem">${esc(t.word)}</b>`;
        speak(t.word, .7);
        setTimeout(() => { round++; nextRound(); }, 2300);
      } else {
        $("#rv").textContent = "¡Casi! Probá otra vez 💪";
        setTimeout(() => { typed = []; busy = false; render(); }, 900);
      }
    }
  };
  const nextRound = () => {
    if (round >= order.length) return finish("write", results.filter(Boolean).length, order.length);
    const t = order[round];
    letters = [...word()].filter(ch => /[a-z]/.test(ch));
    typed = []; tries = 0; busy = false;
    const decoys = shuffle("abcdefghijklmnopqrstuvwxyz".split("").filter(l => !letters.includes(l))).slice(0, 2);
    tiles = shuffle([...letters, ...decoys]);
    $("#we").textContent = t.emoji || "⭐";
    $("#wes").textContent = `"${t.translation}"`;
    $("#ws").onclick = () => speak(t.word, .7);
    $("#rv").textContent = "";
    dots($("#d"), order.length, results, round);
    render();
  };
  const onKey = e => {
    if (e.key === "Backspace") { removeFrom(typed.length - 1); return; }
    const l = e.key.toLowerCase();
    const i = tiles.findIndex((t, idx) => t === l && !typed.includes(idx));
    if (i >= 0) add(i);
  };
  document.addEventListener("keydown", onKey);
  cleanup = () => document.removeEventListener("keydown", onKey);
  $("#clr").onclick = () => { if (!busy) { typed = []; render(); } };
  nextRound();
}

// ------------------------------------------------------------ 5) Desafío final
function quiz() {
  const order = shuffle(WORDS).slice(0, Math.min(6, WORDS.length));
  const results = [];
  let round = 0;
  $("#stage").innerHTML = `<div class="challenge"><div class="dots" id="d"></div><div class="prompt" id="p"></div><div class="opt-grid" id="o"></div></div>`;
  const next = () => {
    if (round >= order.length) return finish("quiz", results.filter(Boolean).length, order.length);
    dots($("#d"), order.length, results, round);
    const t = order[round];
    const opts = shuffle([t, ...others(t, Math.min(3, WORDS.length - 1))]);
    const toEnglish = round % 2 === 0;
    $("#p").innerHTML = toEnglish
      ? `<p class="p-label">🏁 ¿Cómo se dice en inglés…?</p><div class="p-word" style="color:var(--pink)">${esc(t.translation)}</div>`
      : `<p class="p-label">🏁 ¿Qué significa…?</p><div class="p-word">${esc(t.word)}</div>`;
    $("#o").innerHTML = opts.map((o, i) => `<button class="opt" data-i="${i}">${esc(toEnglish ? o.word : o.translation)}</button>`).join("");
    let locked = false;
    $$("#o .opt").forEach(b => b.onclick = () => {
      if (locked) return; locked = true;
      const ok = opts[+b.dataset.i] === t;
      results[round] = ok;
      b.classList.add(ok ? "ok" : "no");
      if (!ok) $$("#o .opt")[opts.indexOf(t)].classList.add("ok");
      beep(ok ? "good" : "bad");
      speak(t.word);
      round++; dots($("#d"), order.length, results, round);
      setTimeout(next, 1400);
    });
  };
  next();
}

// Empieza por la primera actividad sin aprobar
const firstOpen = LS.activities.findIndex(a => !(progress[a] && progress[a].passed));
openActivity(firstOpen >= 0 ? firstOpen : 0);
