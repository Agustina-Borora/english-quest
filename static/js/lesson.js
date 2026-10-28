// Lección: actividades en el orden que eligió la profe.
// Cada paso (STEPS) es una actividad; si la lección va "tema por tema", cada paso usa solo
// las palabras de su tema y el escenario que la profe eligió para ese tema.
const LS = window.LESSON;
const STEPS = LS.steps;
const ALL_WORDS = LS.words;
let WORDS = ALL_WORDS;
let SCENE = LS.scene;
let progress = LS.progress || {};
let current = 0;
let cleanup = null;   // para sacar eventos de teclado al cambiar de actividad

$("#lesson-building").innerHTML = buildingSVG(LS.scene);

const stepName = s => `${s.topic_emoji ? s.topic_emoji + " " : ""}${ACTS[s.activity].emoji} ${ACTS[s.activity].name}`;

function stepper() {
  $("#stepper").innerHTML = STEPS.map((s, i) => {
    const ok = progress[s.key] && progress[s.key].passed;
    const newTopic = s.topic_id && (i === 0 || STEPS[i - 1].topic_id !== s.topic_id);
    return `${newTopic ? `<span class="topic-tag">${esc(s.topic_emoji)} ${esc(s.topic)}</span>` : ""}<button class="${i === current ? "now" : ""}" data-i="${i}"><span class="st">${ok ? "⭐" : "☆"}</span>${ACTS[s.activity].emoji} ${ACTS[s.activity].name}</button>`;
  }).join("");
  $$("#stepper button").forEach(b => b.onclick = () => openActivity(+b.dataset.i));
}

// ------------------------------------------------------------ ¿cómo se juega?
// La primera vez que se abre cada actividad se explica sola; después, con el botón ❓.
const HOWTO = {
  explore: () => [
    "👆 Tocá cada objeto que aparece en la escena.",
    "🔊 Vas a escuchar cómo se dice en inglés y ver qué significa.",
    "➜ Si aparece <b>Más cosas</b>, tocalo: hay más objetos escondidos.",
    "⭐ Cuando descubras <b>todos</b>, ganás la estrella."],
  cards: () => [
    "👆 Tocá la tarjeta para darla vuelta y ver qué significa.",
    "🔊 El botón amarillo repite la palabra, más despacio.",
    "➡ Pasá a la siguiente con la flecha. En la última aparece 🏁.",
    "⭐ Mirá <b>todas</b> las tarjetas para ganar la estrella."],
  read: () => [
    "📖 <b>Leé</b> la palabra en inglés y tocá el dibujo que corresponde.",
    "👂 <b>Escuchá</b> la palabra (tocá 🔊 para repetirla) y tocá cómo se escribe.",
    "✅ Si te equivocás, te muestra en verde la respuesta correcta.",
    `⭐ Acertá al menos <b>${needed(Math.min(6, WORDS.length))} de ${Math.min(6, WORDS.length)}</b> para ganar la estrella.`],
  write: () => [
    "🇦🇷 Te muestro un dibujo y la palabra en castellano.",
    "🔤 Tocá las letras en orden para escribirla en inglés (también podés usar el teclado). ¡Ojo: hay 2 letras que sobran!",
    "↩ Si te equivocás, tocá una letra de arriba o <b>Borrar</b>. Tenés 2 intentos por palabra.",
    `⭐ Las que te salen a la primera cuentan como acierto: necesitás <b>${needed(Math.min(5, WORDS.length))} de ${Math.min(5, WORDS.length)}</b>.`],
  quiz: () => [
    "🏁 Es el repaso final de todo lo que aprendiste.",
    "❓ Hay dos tipos de pregunta: <b>¿Cómo se dice en inglés…?</b> y <b>¿Qué significa…?</b>",
    "👆 Tocá la respuesta correcta.",
    `⭐ Acertá al menos <b>${needed(Math.min(6, WORDS.length))} de ${Math.min(6, WORDS.length)}</b> para ganar la estrella.`],
};
function needed(total) { return Math.ceil(total * 0.6); }

function howto(a) {
  try { localStorage.setItem("howto_" + a, "1"); } catch (e) { /* sin almacenamiento */ }
  modal(`
    <span class="w-emoji">${ACTS[a].emoji}</span>
    <h2>¿Cómo se juega ${ACTS[a].name}?</h2>
    <ul class="howto">${HOWTO[a]().map(x => `<li>${x}</li>`).join("")}</ul>
    <div class="row"><button class="btn green" data-go>¡A jugar! 🚀</button></div>`,
    box => { $("[data-go]", box).onclick = closeModal; });
}
function maybeHowto(a) {
  let seen = false;
  try { seen = localStorage.getItem("howto_" + a) === "1"; } catch (e) { seen = true; }
  if (!seen) howto(a);
}
// Si el tutorial de la pantalla se va a mostrar, la explicación espera a que termine
let tourPending = !!(window.TOUR && window.tourSeen) && !window.tourSeen(window.TOUR.key);
if (window.TOUR) window.TOUR.onEnd = () => { tourPending = false; if (WORDS.length) maybeHowto(STEPS[current].activity); };
const howtoBtn = $("#howto-btn");
if (howtoBtn) howtoBtn.onclick = () => { if (WORDS.length) howto(STEPS[current].activity); };

function openActivity(i) {
  if (cleanup) { cleanup(); cleanup = null; }
  current = i;
  const step = STEPS[i];
  WORDS = step.topic_id ? ALL_WORDS.filter(w => w.topic_id === step.topic_id) : ALL_WORDS;
  SCENE = step.scene || LS.scene;
  stepper();
  $("#below").innerHTML = "";
  if (!WORDS.length) {
    $("#stage").innerHTML = `<div class="challenge"><div class="prompt"><span class="p-emoji">📭</span><p class="p-label">${step.topic_id ? "Este tema" : "Esta lección"} todavía no tiene palabras.</p></div></div>`;
    return;
  }
  const a = step.activity;
  ({ explore, cards, read, write, quiz })[a]();
  if (!tourPending) maybeHowto(a);
}

// ------------------------------------------------------------ resultado y guardado
async function finish(activity, score, total) {
  const key = STEPS[current].key;
  const needed = (activity === "explore" || activity === "cards") ? total : Math.ceil(total * 0.6);
  let passed = score >= needed, coinsWon = score * 5, firstPass = passed && !(progress[key] && progress[key].passed);
  if (!window.PREVIEW) {
    try {
      const r = await postJSON(window.SAVE_URL, { lesson_id: LS.id, activity: key, score, total });
      passed = r.passed; coinsWon = r.coins_won; firstPass = r.first_pass; progress = r.progress;
      $("#coins").textContent = `🪙 ${r.coins}`;
    } catch (e) { toast("No se pudo guardar 😕"); }
  } else if (passed) {
    progress[key] = { passed: true, best: score, total };
  }
  stepper();
  const isLast = current >= STEPS.length - 1;
  const allDone = STEPS.every(s => progress[s.key] && progress[s.key].passed);
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
      ${!isLast ? `<button class="btn green" data-a="next">Siguiente: ${esc(stepName(STEPS[current + 1]))} ➜</button>` : ""}
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
// Para comparar el nombre que la profe le puso a un lugar con una palabra: "La Cabeza" = "cabeza"
const norm = t => String(t || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").trim()
  .replace(/^(el|la|los|las|un|una|the|a|an)\s+/, "");

// Ordena las palabras según los lugares: si un lugar tiene nombre (ej: "cabeza"), va ahí la palabra
// que coincide (en inglés o en castellano); las demás ocupan los lugares libres y las páginas siguientes.
function arrangeWords(words, slots) {
  const first = new Array(slots.length).fill(null), rest = [...words];
  slots.forEach((s, i) => {
    const label = norm(s[2]);
    if (!label) return;
    const k = rest.findIndex(w => norm(w.word) === label || norm(w.translation) === label);
    if (k >= 0) first[i] = rest.splice(k, 1)[0];
  });
  first.forEach((w, i) => { if (!w && rest.length) first[i] = rest.shift(); });
  return [...first, ...rest];
}

function explore() {
  const SLOTS = sceneSlots(SCENE);
  const PAGE = SLOTS.length;
  const ORDER = arrangeWords(WORDS, SLOTS);   // puede tener huecos (null) si hay menos palabras que lugares
  const pages = Math.ceil(ORDER.length / PAGE);
  const seen = new Set();
  let page = 0;
  const draw = () => {
    const items = ORDER.slice(page * PAGE, page * PAGE + PAGE);
    $("#stage").innerHTML = `<div class="scene ${CUSTOM[SCENE] ? "custom" : ""}">${sceneSVG(SCENE)}
      ${items.map((w, i) => w ? `<button class="obj ${seen.has(w.word) ? "seen" : ""}" data-w="${page * PAGE + i}" style="left:${SLOTS[i][0]}%;top:${SLOTS[i][1]}%;animation-delay:${-i * .4}s">${w.emoji || "⭐"}</button>` : "").join("")}
      <div class="guide">${avatarSVG(window.ME)}</div>
      <div class="say-bubble">Tap everything! 👆 <small>Tocá todo</small></div></div>`;
    $("#below").innerHTML = `<div class="bar-row"><span>🔍 Descubiertas: ${seen.size}/${WORDS.length}</span>
      <div class="progress"><div style="width:${seen.size / WORDS.length * 100}%"></div></div>
      ${pages > 1 ? `<button class="btn small ghost" id="pg">${page + 1}/${pages} ➜ Más cosas</button>` : ""}</div>`;
    const pg = $("#pg"); if (pg) pg.onclick = () => { page = (page + 1) % pages; draw(); };
    $$("#stage .obj").forEach(b => b.onclick = () => {
      const w = ORDER[+b.dataset.w];
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
    $("#stage").innerHTML = `<div class="flip-area">${sceneSVG(SCENE)}
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
const firstOpen = STEPS.findIndex(s => !(progress[s.key] && progress[s.key].passed));
openActivity(firstOpen >= 0 ? firstOpen : 0);
