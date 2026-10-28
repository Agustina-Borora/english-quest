// =====================================================================
// Escenarios dibujados en SVG: fondos de las lecciones y edificios del mapa
// =====================================================================
const SCENE_INFO = {
  house: { name: "House", es: "Casa", color: "#ff5fa2" },
  supermarket: { name: "Supermarket", es: "Supermercado", color: "#ff9f1c" },
  school: { name: "School", es: "Escuela", color: "#3a86ff" },
  park: { name: "Park", es: "Parque", color: "#2ecc71" },
  zoo: { name: "Zoo", es: "Zoológico", color: "#f7b500" },
  beach: { name: "Beach", es: "Playa", color: "#0fa3b1" },
};

// Lugares donde se ubican las palabras dentro de cada escena (en %)
const SCENE_SLOTS = [
  [30, 80], [48, 72], [66, 81], [86, 74],
  [14, 42], [34, 54], [56, 52], [78, 50],
  [26, 24], [46, 28], [68, 24], [90, 30],
];

function _clouds(y) {
  return `<g fill="#fff" opacity=".9">
    <g transform="translate(180 ${y})"><ellipse cx="0" cy="0" rx="70" ry="30"/><ellipse cx="50" cy="-18" rx="50" ry="32"/><ellipse cx="100" cy="0" rx="60" ry="26"/></g>
    <g transform="translate(1180 ${y + 40})"><ellipse cx="0" cy="0" rx="60" ry="26"/><ellipse cx="45" cy="-16" rx="44" ry="28"/><ellipse cx="90" cy="0" rx="52" ry="22"/></g></g>`;
}
function _tree(x, y, s = 1, c = "#3fae49") {
  return `<g transform="translate(${x} ${y}) scale(${s})"><rect x="-14" y="-10" width="28" height="90" rx="8" fill="#8a5a3b"/>
    <circle cx="0" cy="-60" r="70" fill="${c}"/><circle cx="-50" cy="-20" r="48" fill="${c}"/><circle cx="50" cy="-24" r="50" fill="${c}"/>
    <circle cx="-20" cy="-80" r="20" fill="#fff" opacity=".15"/></g>`;
}
function _flowers(y, n = 12) {
  let s = "";
  const cols = ["#ff5fa2", "#ffd23f", "#fff", "#9b5de5"];
  for (let i = 0; i < n; i++) {
    const x = 60 + i * (1500 / n) + (i % 3) * 20;
    const yy = y + (i % 2) * 40;
    s += `<g transform="translate(${x} ${yy})"><line x1="0" y1="0" x2="0" y2="26" stroke="#2e8b3e" stroke-width="4"/>
      <circle r="9" fill="${cols[i % 4]}"/><circle r="4" fill="#ffb703"/></g>`;
  }
  return s;
}

const SCENE_BG = {
  house: () => `
    <rect width="1600" height="1000" fill="#ffe3ec"/>
    <g fill="#ffc2d4" opacity=".7">${Array.from({ length: 60 }, (_, i) => `<circle cx="${(i % 12) * 140 + ((Math.floor(i / 12) % 2) * 70) + 40}" cy="${Math.floor(i / 12) * 130 + 50}" r="10"/>`).join("")}</g>
    <rect y="640" width="1600" height="360" fill="#e0a875"/>
    ${Array.from({ length: 8 }, (_, i) => `<line x1="0" y1="${680 + i * 45}" x2="1600" y2="${680 + i * 45}" stroke="#c98d5b" stroke-width="4"/>`).join("")}
    <rect y="620" width="1600" height="26" fill="#fff"/>
    <g transform="translate(150 120)"><rect width="300" height="260" rx="12" fill="#8fd3ff" stroke="#fff" stroke-width="18"/>
      <line x1="150" y1="0" x2="150" y2="260" stroke="#fff" stroke-width="12"/><line x1="0" y1="130" x2="300" y2="130" stroke="#fff" stroke-width="12"/>
      <circle cx="230" cy="70" r="34" fill="#ffd23f"/>
      <path d="M-30 -20 Q60 120 -10 300 L-50 300 L-50 -20 Z" fill="#ff5fa2"/><path d="M330 -20 Q240 120 310 300 L350 300 L350 -20 Z" fill="#ff5fa2"/>
      <rect x="-60" y="-34" width="420" height="18" rx="9" fill="#9b5de5"/></g>
    <g transform="translate(1080 140)"><rect width="230" height="170" rx="10" fill="#fff" stroke="#c98d5b" stroke-width="14"/>
      <path d="M20 150 L90 60 L140 120 L170 90 L210 150 Z" fill="#2ecc71"/><circle cx="170" cy="45" r="20" fill="#ffd23f"/></g>
    <ellipse cx="800" cy="860" rx="520" ry="90" fill="#9b5de5" opacity=".35"/>
    <ellipse cx="800" cy="860" rx="440" ry="65" fill="#ff5fa2" opacity=".25"/>`,

  supermarket: () => `
    <rect width="1600" height="1000" fill="#e8fbff"/>
    <rect y="0" width="1600" height="90" fill="#ff9f1c"/>
    <text x="800" y="64" font-family="Fredoka, Arial" font-weight="700" font-size="54" fill="#fff" text-anchor="middle">SUPERMARKET</text>
    ${Array.from({ length: 16 }, (_, i) => `<path d="M${i * 100} 90 h100 l-10 40 h-80 Z" fill="${i % 2 ? "#ff9f1c" : "#fff"}"/>`).join("")}
    ${[0, 1].map(k => `<g transform="translate(${k ? 860 : 80} 180)">
      <rect width="660" height="430" rx="14" fill="#b5651d"/><rect x="18" y="18" width="624" height="394" fill="#fde2c4"/>
      ${[120, 250, 380].map(y => `<rect x="10" y="${y}" width="640" height="16" fill="#b5651d"/>`).join("")}
      ${Array.from({ length: 24 }, (_, i) => { const row = Math.floor(i / 8); const cols = ["#ff4d6d", "#3a86ff", "#2ecc71", "#ffd23f", "#9b5de5", "#ff9f1c"];
        return `<rect x="${32 + (i % 8) * 76}" y="${46 + row * 130}" width="58" height="${70 - (i % 3) * 10}" rx="8" fill="${cols[(i + k) % 6]}" transform="translate(0 ${(i % 3) * 10})"/>`; }).join("")}
    </g>`).join("")}
    <rect y="640" width="1600" height="360" fill="#cfeff3"/>
    ${Array.from({ length: 64 }, (_, i) => `<rect x="${(i % 16) * 100}" y="${640 + Math.floor(i / 16) * 90}" width="100" height="90" fill="${(i + Math.floor(i / 16)) % 2 ? "#b8e4ea" : "#e6fafc"}"/>`).join("")}`,

  school: () => `
    <rect width="1600" height="1000" fill="#fff3c4"/>
    <g>${Array.from({ length: 13 }, (_, i) => `<path d="M${i * 130} 20 l65 60 l65 -60" fill="${["#ff5fa2", "#3a86ff", "#2ecc71", "#ff9f1c"][i % 4]}"/>
      <text x="${i * 130 + 65}" y="58" font-family="Fredoka, Arial" font-weight="700" font-size="26" fill="#fff" text-anchor="middle">${"ABCDEFGHIJKLM"[i]}</text>`).join("")}
      <line x1="0" y1="20" x2="1600" y2="20" stroke="#8a5a3b" stroke-width="4"/></g>
    <g transform="translate(330 130)"><rect width="940" height="400" rx="16" fill="#8a5a3b"/><rect x="22" y="22" width="896" height="356" rx="8" fill="#2f6e4f"/>
      <text x="90" y="150" font-family="Fredoka, Arial" font-size="96" fill="#fff" opacity=".9">Hello!</text>
      <text x="560" y="140" font-family="Fredoka, Arial" font-size="70" fill="#ffd23f" opacity=".9">A B C</text>
      <text x="560" y="250" font-family="Fredoka, Arial" font-size="70" fill="#ff8ab9" opacity=".9">1 2 3</text>
      <path d="M90 230 Q250 300 420 220" stroke="#fff" stroke-width="6" fill="none" opacity=".7"/>
      <rect x="380" y="378" width="180" height="20" rx="6" fill="#c98d5b"/><rect x="400" y="370" width="40" height="12" rx="3" fill="#fff"/></g>
    <g transform="translate(1400 220)"><circle r="80" fill="#fff" stroke="#ff5fa2" stroke-width="14"/>
      <line x1="0" y1="0" x2="0" y2="-52" stroke="#2b1663" stroke-width="8" stroke-linecap="round"/><line x1="0" y1="0" x2="38" y2="10" stroke="#2b1663" stroke-width="8" stroke-linecap="round"/></g>
    <rect y="640" width="1600" height="360" fill="#c9a66b"/>
    ${Array.from({ length: 8 }, (_, i) => `<line x1="${i * 220}" y1="640" x2="${i * 220 - 120}" y2="1000" stroke="#b08850" stroke-width="5"/>`).join("")}`,

  park: () => `
    <defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8fd3ff"/><stop offset="1" stop-color="#d6f2ff"/></linearGradient></defs>
    <rect width="1600" height="1000" fill="url(#sky)"/>
    <circle cx="1400" cy="130" r="80" fill="#ffd23f"/><circle cx="1400" cy="130" r="110" fill="#ffd23f" opacity=".25"/>
    ${_clouds(150)}
    <path d="M0 520 Q300 400 650 500 Q1000 600 1300 470 Q1480 410 1600 470 L1600 1000 L0 1000 Z" fill="#8bd46e"/>
    <path d="M0 640 Q400 560 800 640 Q1200 720 1600 620 L1600 1000 L0 1000 Z" fill="#6cc24a"/>
    <path d="M700 1000 Q760 820 820 700 Q860 640 980 640" stroke="#e8d3a3" stroke-width="90" fill="none" stroke-linecap="round"/>
    ${_tree(150, 520, 1.1)}${_tree(1450, 560, 1.2, "#34a853")}${_tree(1150, 470, .7, "#57c26a")}
    <g transform="translate(1180 760)"><rect width="260" height="22" rx="6" fill="#b5651d"/><rect y="40" width="260" height="22" rx="6" fill="#b5651d"/>
      <rect x="20" y="62" width="16" height="60" fill="#7a4a2a"/><rect x="224" y="62" width="16" height="60" fill="#7a4a2a"/></g>
    ${_flowers(860)}`,

  zoo: () => `
    <defs><linearGradient id="zsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#ffd59e"/><stop offset="1" stop-color="#fff1d6"/></linearGradient></defs>
    <rect width="1600" height="1000" fill="url(#zsky)"/>
    <circle cx="260" cy="150" r="80" fill="#ff9f1c" opacity=".8"/>
    ${_clouds(120)}
    <path d="M0 560 Q400 470 800 540 Q1200 610 1600 520 L1600 1000 L0 1000 Z" fill="#a8d672"/>
    <rect y="700" width="1600" height="300" fill="#8cc152"/>
    ${_tree(120, 560, .9, "#5aa832")}${_tree(1480, 540, 1, "#4f9a2b")}
    <g transform="translate(560 180)"><rect x="0" y="40" width="40" height="440" fill="#8a5a3b"/><rect x="440" y="40" width="40" height="440" fill="#8a5a3b"/>
      <path d="M-20 60 Q240 -60 500 60 L500 120 Q240 0 -20 120 Z" fill="#2ecc71"/>
      <text x="240" y="92" font-family="Fredoka, Arial" font-weight="700" font-size="80" fill="#fff" text-anchor="middle">ZOO</text></g>
    ${Array.from({ length: 33 }, (_, i) => `<rect x="${i * 50}" y="600" width="18" height="120" rx="6" fill="#c98d5b"/>`).join("")}
    <rect y="630" width="1600" height="14" fill="#a8743f"/><rect y="680" width="1600" height="14" fill="#a8743f"/>
    <ellipse cx="300" cy="880" rx="200" ry="60" fill="#5bc0eb" opacity=".8"/>
    <g fill="#9e9e9e"><ellipse cx="1300" cy="860" rx="120" ry="60"/><ellipse cx="1400" cy="880" rx="80" ry="45" fill="#b5b5b5"/></g>`,

  beach: () => `
    <defs><linearGradient id="bsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5ec8ff"/><stop offset="1" stop-color="#c9efff"/></linearGradient></defs>
    <rect width="1600" height="1000" fill="url(#bsky)"/>
    <circle cx="1350" cy="150" r="90" fill="#ffd23f"/>
    ${_clouds(130)}
    <rect y="430" width="1600" height="260" fill="#1fa2d6"/>
    ${Array.from({ length: 4 }, (_, r) => Array.from({ length: 12 }, (_, i) => `<path d="M${i * 140 + (r % 2) * 70} ${470 + r * 55} q35 -22 70 0" stroke="#fff" stroke-width="6" fill="none" opacity=".6"/>`).join("")).join("")}
    <g transform="translate(1050 420)"><path d="M0 0 L160 0 L130 40 L30 40 Z" fill="#ff4d6d"/><rect x="72" y="-120" width="8" height="120" fill="#555"/><path d="M80 -120 L80 -20 L150 -30 Z" fill="#fff"/></g>
    <path d="M0 640 Q400 600 800 650 Q1200 700 1600 630 L1600 1000 L0 1000 Z" fill="#f6d79b"/>
    <g transform="translate(220 560)"><path d="M0 0 Q20 -200 70 -330" stroke="#8a5a3b" stroke-width="30" fill="none" stroke-linecap="round"/>
      <g transform="translate(70 -330)" fill="#2ecc71"><path d="M0 0 Q-120 -40 -200 40 Q-100 0 0 10Z"/><path d="M0 0 Q120 -50 210 30 Q110 -5 0 10Z"/><path d="M0 0 Q-40 -110 -140 -130 Q-50 -60 -5 5Z"/><path d="M0 0 Q60 -110 160 -120 Q60 -50 5 5Z"/></g></g>
    <g transform="translate(1250 700)"><path d="M-160 0 Q0 -150 160 0 Z" fill="#ff5fa2"/><path d="M-160 0 Q-80 -110 0 -150 Q-40 -70 -53 0 Z" fill="#fff" opacity=".6"/><path d="M53 0 Q40 -70 0 -150 Q80 -110 160 0 Z" fill="#fff" opacity=".6"/><rect x="-5" y="0" width="10" height="200" fill="#8a5a3b"/></g>`,
};

// Escenarios que creó la profe con sus imágenes (vienen del servidor en window.CUSTOM_SCENES)
const CUSTOM = window.CUSTOM_SCENES || {};
Object.entries(CUSTOM).forEach(([k, c]) => { SCENE_INFO[k] = { name: c.name, es: c.name, color: "#5b2bd6" }; });

function sceneSlots(scene) {
  const c = CUSTOM[scene];
  return c && c.slots && c.slots.length ? c.slots : SCENE_SLOTS;
}

function sceneSVG(scene) {
  const c = CUSTOM[scene];
  if (c) return `<img class="scene-bg" src="${esc(c.img)}" alt="${esc(c.name)}">`;
  const draw = SCENE_BG[scene] || SCENE_BG.house;
  return `<svg class="scene-bg" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">${draw()}</svg>`;
}

// ---------- Edificios del mapa (viewBox 0 0 200 200)
const BUILDINGS = {
  house: `<ellipse cx="100" cy="186" rx="80" ry="12" fill="#000" opacity=".15"/>
    <rect x="132" y="38" width="20" height="44" fill="#a33b3b"/>
    <rect x="38" y="88" width="124" height="96" rx="6" fill="#ffd6e0"/>
    <path d="M24 96 L100 28 L176 96 Z" fill="#ff4d6d"/><path d="M24 96 L100 28 L176 96" fill="none" stroke="#c9184a" stroke-width="8" stroke-linejoin="round"/>
    <rect x="84" y="128" width="34" height="56" rx="6" fill="#9b5de5"/><circle cx="110" cy="158" r="3" fill="#ffd23f"/>
    <rect x="50" y="112" width="26" height="26" rx="4" fill="#8fd3ff" stroke="#fff" stroke-width="4"/><rect x="126" y="112" width="26" height="26" rx="4" fill="#8fd3ff" stroke="#fff" stroke-width="4"/>`,
  supermarket: `<ellipse cx="100" cy="186" rx="88" ry="12" fill="#000" opacity=".15"/>
    <rect x="16" y="70" width="168" height="114" rx="6" fill="#fff1d6"/>
    <rect x="10" y="44" width="180" height="34" rx="8" fill="#ff9f1c"/>
    <text x="100" y="69" font-family="Fredoka, Arial" font-weight="700" font-size="22" fill="#fff" text-anchor="middle">MARKET</text>
    ${Array.from({ length: 9 }, (_, i) => `<path d="M${16 + i * 18.6} 78 h18.6 v14 q-9.3 10 -18.6 0 Z" fill="${i % 2 ? "#ff4d6d" : "#fff"}"/>`).join("")}
    <rect x="30" y="108" width="54" height="76" rx="4" fill="#8fd3ff" stroke="#fff" stroke-width="4"/>
    <rect x="98" y="108" width="72" height="44" rx="4" fill="#8fd3ff" stroke="#fff" stroke-width="4"/>
    <circle cx="120" cy="136" r="9" fill="#ff4d6d"/><circle cx="138" cy="138" r="8" fill="#ffd23f"/><circle cx="155" cy="136" r="9" fill="#2ecc71"/>`,
  school: `<ellipse cx="100" cy="186" rx="88" ry="12" fill="#000" opacity=".15"/>
    <rect x="14" y="86" width="172" height="98" rx="6" fill="#ffe08a"/>
    <path d="M56 86 L100 36 L144 86 Z" fill="#3a86ff"/><rect x="70" y="80" width="60" height="104" fill="#fff3c4"/>
    <circle cx="100" cy="100" r="14" fill="#fff" stroke="#3a86ff" stroke-width="4"/><path d="M100 100 L100 92 M100 100 L106 103" stroke="#2b1663" stroke-width="3" stroke-linecap="round"/>
    <rect x="88" y="140" width="24" height="44" rx="4" fill="#ff5fa2"/>
    <line x1="100" y1="36" x2="100" y2="10" stroke="#555" stroke-width="4"/><path d="M100 10 L126 18 L100 26 Z" fill="#ff4d6d"/>
    ${[26, 146].map(x => `<rect x="${x}" y="106" width="26" height="22" rx="3" fill="#8fd3ff" stroke="#fff" stroke-width="3"/><rect x="${x}" y="142" width="26" height="22" rx="3" fill="#8fd3ff" stroke="#fff" stroke-width="3"/>`).join("")}`,
  park: `<ellipse cx="100" cy="186" rx="88" ry="12" fill="#000" opacity=".15"/>
    <rect x="92" y="110" width="16" height="74" rx="6" fill="#8a5a3b"/>
    <circle cx="100" cy="82" r="50" fill="#34a853"/><circle cx="66" cy="108" r="32" fill="#3fae49"/><circle cx="134" cy="108" r="34" fill="#3fae49"/>
    <circle cx="84" cy="62" r="12" fill="#fff" opacity=".2"/>
    <rect x="128" y="158" width="58" height="8" rx="3" fill="#b5651d"/><rect x="128" y="146" width="58" height="8" rx="3" fill="#b5651d"/>
    <rect x="134" y="166" width="6" height="18" fill="#7a4a2a"/><rect x="174" y="166" width="6" height="18" fill="#7a4a2a"/>
    ${[[24, 176, "#ff5fa2"], [40, 182, "#ffd23f"], [56, 176, "#fff"]].map(([x, y, c]) => `<circle cx="${x}" cy="${y}" r="7" fill="${c}"/><circle cx="${x}" cy="${y}" r="3" fill="#ff9f1c"/>`).join("")}`,
  zoo: `<ellipse cx="100" cy="186" rx="88" ry="12" fill="#000" opacity=".15"/>
    <rect x="22" y="70" width="20" height="114" fill="#8a5a3b"/><rect x="158" y="70" width="20" height="114" fill="#8a5a3b"/>
    <path d="M12 86 Q100 20 188 86 L188 110 Q100 46 12 110 Z" fill="#2ecc71"/>
    <text x="100" y="92" font-family="Fredoka, Arial" font-weight="700" font-size="30" fill="#fff" text-anchor="middle">ZOO</text>
    <g transform="translate(92 98)"><rect x="6" y="20" width="12" height="60" rx="5" fill="#f7b500"/><ellipse cx="12" cy="18" rx="16" ry="10" fill="#f7b500"/>
      <circle cx="8" cy="40" r="3" fill="#a0602b"/><circle cx="14" cy="56" r="3" fill="#a0602b"/><circle cx="6" cy="16" r="2" fill="#2b1663"/></g>
    ${Array.from({ length: 6 }, (_, i) => `<rect x="${46 + i * 19}" y="150" width="8" height="34" rx="3" fill="#c98d5b"/>`).join("")}`,
  beach: `<ellipse cx="100" cy="186" rx="88" ry="12" fill="#000" opacity=".15"/>
    <path d="M10 160 Q100 140 190 160 L190 184 L10 184 Z" fill="#f6d79b"/>
    <path d="M10 150 q20 -12 40 0 q20 12 40 0 q20 -12 40 0 q20 12 40 0 q20 -12 30 -6 L190 160 Q100 140 10 160 Z" fill="#1fa2d6"/>
    <path d="M60 164 Q80 80 76 48" stroke="#8a5a3b" stroke-width="10" fill="none" stroke-linecap="round"/>
    <g transform="translate(76 48)" fill="#2ecc71"><path d="M0 0 Q-40 -14 -66 14 Q-34 0 0 4Z"/><path d="M0 0 Q40 -16 70 10 Q36 -2 0 4Z"/><path d="M0 0 Q-12 -36 -46 -42 Q-16 -20 -2 2Z"/><path d="M0 0 Q20 -36 54 -38 Q20 -16 2 2Z"/></g>
    <g transform="translate(140 120)"><path d="M-40 0 Q0 -44 40 0 Z" fill="#ff5fa2"/><rect x="-2" y="0" width="4" height="56" fill="#555"/></g>`,
};

function buildingSVG(scene) {
  const c = CUSTOM[scene];
  if (c) return `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><defs><clipPath id="cb-${esc(scene)}"><rect x="20" y="20" width="160" height="160" rx="34"/></clipPath></defs>
    <ellipse cx="100" cy="188" rx="80" ry="10" fill="#000" opacity=".15"/>
    <image href="${esc(c.img)}" x="20" y="20" width="160" height="160" preserveAspectRatio="xMidYMid slice" clip-path="url(#cb-${esc(scene)})"/>
    <rect x="20" y="20" width="160" height="160" rx="34" fill="none" stroke="#fff" stroke-width="10"/></svg>`;
  return `<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">${BUILDINGS[scene] || BUILDINGS.house}</svg>`;
}
