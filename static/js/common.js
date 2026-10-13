// Funciones compartidas por todas las pantallas
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

function esc(text) {
  const d = document.createElement("div");
  d.textContent = text == null ? "" : String(text);
  return d.innerHTML;
}

function showScreen(id) {
  $$(".screen").forEach(s => s.classList.add("hidden"));
  const el = document.getElementById(id);
  if (el) el.classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function toast(msg, ms = 2600) {
  const t = document.createElement("div");
  t.className = "toast";
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), ms);
}

function confetti(amount = 120) {
  const colors = ["#ff5fa2", "#ffd23f", "#2ecc71", "#3a86ff", "#ff9f1c", "#9b5de5", "#ffffff"];
  for (let i = 0; i < amount; i++) {
    const c = document.createElement("div");
    c.className = "confetti";
    c.style.left = Math.random() * 100 + "vw";
    c.style.background = colors[i % colors.length];
    c.style.animationDuration = 2 + Math.random() * 2.5 + "s";
    c.style.animationDelay = Math.random() * 0.8 + "s";
    document.body.appendChild(c);
    setTimeout(() => c.remove(), 5500);
  }
}

// Pronunciación en inglés con la voz del navegador (Web Speech API)
let englishVoice = null;
function pickVoice() {
  if (!("speechSynthesis" in window)) return;
  const voices = speechSynthesis.getVoices();
  englishVoice = voices.find(v => v.lang === "en-US") || voices.find(v => v.lang && v.lang.startsWith("en")) || null;
}
if ("speechSynthesis" in window) { pickVoice(); speechSynthesis.onvoiceschanged = pickVoice; }
function speak(text, rate = 0.85) {
  if (!("speechSynthesis" in window) || !text) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "en-US";
  u.rate = rate;
  if (englishVoice) u.voice = englishVoice;
  speechSynthesis.speak(u);
}

// Sonidos cortitos con Web Audio (sin archivos)
let audioCtx = null;
function beep(type = "good") {
  try {
    audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
    const notes = type === "good" ? [523, 659, 784] : type === "bad" ? [300, 220] : type === "win" ? [523, 659, 784, 1046] : [440];
    notes.forEach((f, i) => {
      const o = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      o.type = type === "bad" ? "sawtooth" : "triangle";
      o.frequency.value = f;
      const t = audioCtx.currentTime + i * 0.11;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.exponentialRampToValueAtTime(0.16, t + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.18);
      o.connect(g).connect(audioCtx.destination);
      o.start(t);
      o.stop(t + 0.2);
    });
  } catch (e) { /* sin sonido */ }
}

const SHAPES = ["▲", "◆", "●", "■"];

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

async function postJSON(url, data) {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data) });
  let json = {};
  try { json = await res.json(); } catch (e) {}
  if (!res.ok) throw new Error(json.error || "Error al guardar");
  return json;
}

// Temporizador con barra (lo usan la profe y el alumno en la clase rápida)
function runTimer(fillEl, numEl, seconds, store) {
  clearInterval(store.timer);
  const end = Date.now() + seconds * 1000;
  fillEl.style.transition = "none";
  fillEl.style.width = "100%";
  requestAnimationFrame(() => requestAnimationFrame(() => {
    fillEl.style.transition = `width ${seconds}s linear`;
    fillEl.style.width = "0%";
  }));
  const tick = () => { numEl.textContent = Math.max(0, Math.ceil((end - Date.now()) / 1000)); };
  tick();
  store.timer = setInterval(tick, 250);
}
