// =====================================================================
// Personitas: dibuja un personaje en SVG a partir de sus opciones.
// avatarSVG(avatar, {bust: true}) -> solo cabeza y hombros (para listas)
// =====================================================================
const AVATAR_OPTIONS = {
  skin: ["#ffe0c7", "#f5c9a6", "#e0ac83", "#c68863", "#9b6542", "#6e4529"],
  hairColor: ["#2b1b12", "#5a3214", "#a0602b", "#e8b04a", "#d9442e", "#9b5de5", "#3a86ff", "#ff5fa2"],
  topColor: ["#ff5fa2", "#3a86ff", "#2ecc71", "#ff9f1c", "#9b5de5", "#ffd23f", "#ff4d6d", "#0fa3b1"],
  pantsColor: ["#3d5a99", "#2b1663", "#6b4f3a", "#555c66", "#e85d75"],
  hair: ["Corto", "Largo", "Rulos", "Colita", "Rodetes", "Parado", "Trenzas"],
  eyes: ["Normales", "Felices", "Brillantes"],
  top: ["Remera", "Rayada", "Buzo", "Vestido", "Campera"],
  accessory: ["Nada", "Anteojos", "Gorra", "Moño", "Auriculares", "Corona"],
};

function _pick(list, i) { return list[((i % list.length) + list.length) % list.length]; }

function _shade(hex, amt) {
  const n = parseInt(hex.slice(1), 16);
  const c = v => Math.max(0, Math.min(255, v + amt));
  const r = c(n >> 16), g = c((n >> 8) & 255), b = c(n & 255);
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

function avatarSVG(a, opts = {}) {
  a = Object.assign({ skin: 1, hair: 0, hairColor: 0, eyes: 0, top: 0, topColor: 1, pants: 0, accessory: 0 }, a || {});
  const skin = _pick(AVATAR_OPTIONS.skin, a.skin);
  const skinD = _shade(skin, -28);
  const hc = _pick(AVATAR_OPTIONS.hairColor, a.hairColor);
  const hcD = _shade(hc, -25);
  const tc = _pick(AVATAR_OPTIONS.topColor, a.topColor);
  const tcD = _shade(tc, -30);
  const pc = _pick(AVATAR_OPTIONS.pantsColor, a.pants);
  const hair = a.hair % AVATAR_OPTIONS.hair.length;
  const top = a.top % AVATAR_OPTIONS.top.length;
  const acc = a.accessory % AVATAR_OPTIONS.accessory.length;
  const eyes = a.eyes % AVATAR_OPTIONS.eyes.length;
  const dress = top === 3;

  let s = "";
  // ---------- pelo de atrás
  const back = {
    1: `<path d="M30 44 Q29 14 60 14 Q91 14 90 44 L93 100 Q76 108 60 103 Q44 108 27 100 Z" fill="${hc}"/>`,
    2: `<circle cx="31" cy="54" r="11" fill="${hc}"/><circle cx="89" cy="54" r="11" fill="${hc}"/><circle cx="34" cy="68" r="9" fill="${hc}"/><circle cx="86" cy="68" r="9" fill="${hc}"/>`,
    3: `<path d="M84 30 Q108 38 100 78 Q96 56 82 46 Z" fill="${hc}"/><circle cx="88" cy="30" r="10" fill="${hc}"/>`,
    4: `<circle cx="33" cy="21" r="12" fill="${hc}"/><circle cx="87" cy="21" r="12" fill="${hc}"/>`,
    6: `<path d="M31 50 Q24 72 30 96 Q36 98 38 94 Q34 72 38 54 Z" fill="${hc}"/><path d="M89 50 Q96 72 90 96 Q84 98 82 94 Q86 72 82 54 Z" fill="${hc}"/>
        <circle cx="34" cy="98" r="5" fill="${tc}"/><circle cx="86" cy="98" r="5" fill="${tc}"/>`,
  };
  s += back[hair] || "";

  // ---------- piernas y zapatos
  if (dress) {
    s += `<rect x="45" y="128" width="11" height="24" rx="5" fill="${skin}"/><rect x="64" y="128" width="11" height="24" rx="5" fill="${skin}"/>`;
  } else {
    s += `<rect x="40" y="114" width="40" height="14" rx="4" fill="${pc}"/>
          <rect x="40" y="118" width="18" height="34" rx="5" fill="${pc}"/><rect x="62" y="118" width="18" height="34" rx="5" fill="${pc}"/>`;
  }
  s += `<ellipse cx="49" cy="154" rx="11" ry="6" fill="#33334d"/><ellipse cx="71" cy="154" rx="11" ry="6" fill="#33334d"/>
        <ellipse cx="46" cy="152" rx="4" ry="2" fill="#fff" opacity=".35"/><ellipse cx="68" cy="152" rx="4" ry="2" fill="#fff" opacity=".35"/>`;

  // ---------- brazos
  s += `<rect x="24" y="80" width="14" height="22" rx="7" fill="${top === 4 ? tcD : tc}"/>
        <rect x="82" y="80" width="14" height="22" rx="7" fill="${top === 4 ? tcD : tc}"/>
        <rect x="26" y="96" width="10" height="22" rx="5" fill="${skin}"/><rect x="84" y="96" width="10" height="22" rx="5" fill="${skin}"/>
        <circle cx="31" cy="120" r="6" fill="${skin}"/><circle cx="89" cy="120" r="6" fill="${skin}"/>`;

  // ---------- torso / ropa
  const torso = `M36 88 Q36 77 47 77 L73 77 Q84 77 84 88 L84 122 L36 122 Z`;
  if (top === 2) s += `<path d="M44 74 Q60 92 76 74 L80 82 Q60 100 40 82 Z" fill="${tcD}"/>`; // capucha
  s += `<path d="${torso}" fill="${tc}"/>`;
  if (top === 1) {
    s += `<rect x="36" y="88" width="48" height="5" fill="#fff" opacity=".55"/><rect x="36" y="99" width="48" height="5" fill="#fff" opacity=".55"/><rect x="36" y="110" width="48" height="5" fill="#fff" opacity=".55"/>`;
  }
  if (top === 2) {
    s += `<path d="M47 104 L73 104 L76 118 L44 118 Z" fill="${tcD}" opacity=".7"/>
          <line x1="55" y1="80" x2="54" y2="96" stroke="#fff" stroke-width="2" stroke-linecap="round"/><line x1="65" y1="80" x2="66" y2="96" stroke="#fff" stroke-width="2" stroke-linecap="round"/>`;
  }
  if (dress) {
    s += `<path d="M38 108 L82 108 L94 142 Q60 150 26 142 Z" fill="${tc}"/><path d="M38 108 L82 108 L83 113 L37 113 Z" fill="${tcD}"/>
          <circle cx="50" cy="128" r="3" fill="#fff" opacity=".6"/><circle cx="70" cy="132" r="3" fill="#fff" opacity=".6"/><circle cx="60" cy="122" r="3" fill="#fff" opacity=".6"/>`;
  }
  if (top === 4) {
    s += `<path d="M52 77 L68 77 L66 122 L54 122 Z" fill="#fff"/><path d="M36 88 Q36 77 47 77 L54 77 L56 122 L36 122 Z" fill="${tcD}"/>
          <path d="M84 88 Q84 77 73 77 L66 77 L64 122 L84 122 Z" fill="${tcD}"/><circle cx="60" cy="96" r="4" fill="${tc}"/>`;
  }
  if (top === 0) s += `<path d="M50 77 Q60 86 70 77" fill="none" stroke="${tcD}" stroke-width="3"/><path d="M60 92 L63 99 L71 99.5 L65 104.5 L67 112 L60 108 L53 112 L55 104.5 L49 99.5 L57 99 Z" fill="#ffd23f"/>`;

  // ---------- cuello, orejas y cabeza
  s += `<rect x="53" y="66" width="14" height="14" rx="4" fill="${skinD}"/>
        <circle cx="33" cy="50" r="6" fill="${skin}"/><circle cx="87" cy="50" r="6" fill="${skin}"/>
        <circle cx="60" cy="47" r="27" fill="${skin}"/>`;

  // ---------- cara
  const eyesSvg = [
    `<circle cx="50" cy="49" r="3.4" fill="#2b1663"/><circle cx="70" cy="49" r="3.4" fill="#2b1663"/>`,
    `<path d="M45 50 Q50 44 55 50" fill="none" stroke="#2b1663" stroke-width="3" stroke-linecap="round"/><path d="M65 50 Q70 44 75 50" fill="none" stroke="#2b1663" stroke-width="3" stroke-linecap="round"/>`,
    `<ellipse cx="50" cy="49" rx="5" ry="6" fill="#2b1663"/><ellipse cx="70" cy="49" rx="5" ry="6" fill="#2b1663"/><circle cx="52" cy="46.5" r="2" fill="#fff"/><circle cx="72" cy="46.5" r="2" fill="#fff"/>`,
  ][eyes];
  s += eyesSvg + `
    <path d="M45 41 Q50 38 55 41" fill="none" stroke="${hcD}" stroke-width="2" stroke-linecap="round"/>
    <path d="M65 41 Q70 38 75 41" fill="none" stroke="${hcD}" stroke-width="2" stroke-linecap="round"/>
    <ellipse cx="43" cy="58" rx="5" ry="3" fill="#ff7aa8" opacity=".45"/><ellipse cx="77" cy="58" rx="5" ry="3" fill="#ff7aa8" opacity=".45"/>
    <path d="M52 59 Q60 67 68 59" fill="#c0395f" stroke="#2b1663" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>`;

  // ---------- pelo de adelante
  const bangs = `M33 46 Q31 17 60 16 Q89 17 87 46 Q84 32 72 29 Q62 36 47 30 Q37 34 33 46 Z`;
  const front = {
    0: `<path d="${bangs}" fill="${hc}"/>`,
    1: `<path d="M32 50 Q30 16 60 15 Q90 16 88 50 Q86 30 74 27 Q60 38 44 28 Q34 32 32 50 Z" fill="${hc}"/>`,
    2: [[36, 38, 10], [40, 26, 11], [51, 19, 11], [63, 17, 11], [75, 21, 11], [83, 30, 10], [86, 41, 9]]
         .map(([x, y, r]) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${hc}"/>`).join(""),
    3: `<path d="${bangs}" fill="${hc}"/><circle cx="84" cy="30" r="5" fill="${tc}"/>`,
    4: `<path d="${bangs}" fill="${hc}"/>`,
    5: `<path d="M32 47 L29 29 L40 33 L41 16 L52 27 L58 10 L66 26 L77 14 L79 31 L91 27 L88 47 Q82 32 60 33 Q39 32 32 47 Z" fill="${hc}"/>`,
    6: `<path d="M32 48 Q30 16 60 15 Q90 16 88 48 Q80 28 60 30 Q40 28 32 48 Z" fill="${hc}"/><line x1="60" y1="16" x2="60" y2="30" stroke="${hcD}" stroke-width="2"/>`,
  };
  s += front[hair] || front[0];
  s += `<path d="M44 24 Q52 19 60 20" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity=".35"/>`;

  // ---------- accesorios
  const accSvg = {
    1: `<g fill="none" stroke="#2b1663" stroke-width="2.5"><circle cx="50" cy="49" r="8" fill="#fff" fill-opacity=".25"/><circle cx="70" cy="49" r="8" fill="#fff" fill-opacity=".25"/><path d="M58 49 L62 49 M42 48 L34 46 M78 48 L86 46"/></g>`,
    2: `<path d="M32 36 Q32 12 60 12 Q88 12 88 36 Z" fill="#ff4d6d"/><path d="M60 34 L98 34 Q100 40 92 40 L60 40 Z" fill="#c9184a"/><circle cx="60" cy="13" r="3" fill="#c9184a"/>`,
    3: `<g transform="translate(36 22) rotate(-18)"><path d="M0 0 L-12 -8 L-12 8 Z M0 0 L12 -8 L12 8 Z" fill="#ff5fa2"/><circle r="4" fill="#ff8ab9"/></g>`,
    4: `<path d="M31 46 Q31 12 60 12 Q89 12 89 46" fill="none" stroke="#2b1663" stroke-width="5"/><rect x="25" y="40" width="12" height="18" rx="5" fill="#ff4d6d"/><rect x="83" y="40" width="12" height="18" rx="5" fill="#ff4d6d"/>`,
    5: `<path d="M40 22 L44 6 L52 16 L60 2 L68 16 L76 6 L80 22 Z" fill="#ffd23f" stroke="#f7a400" stroke-width="2" stroke-linejoin="round"/><circle cx="60" cy="14" r="2.5" fill="#ff4d6d"/>`,
  };
  s += accSvg[acc] || "";

  const vb = opts.bust ? "14 0 92 92" : "8 -2 104 166";
  const cls = opts.className ? ` class="${opts.className}"` : "";
  return `<svg${cls} viewBox="${vb}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="personaje">${s}</svg>`;
}

// Pinta todos los elementos <span data-avatar='{...}'> de la página
function paintAvatars(root = document) {
  root.querySelectorAll("[data-avatar]").forEach(el => {
    let data = {};
    try { data = JSON.parse(el.dataset.avatar || "{}"); } catch (e) {}
    el.innerHTML = avatarSVG(data, { bust: el.dataset.bust !== undefined });
  });
}
document.addEventListener("DOMContentLoaded", () => paintAvatars());
