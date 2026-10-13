// Clase rápida - pantalla de la profe (proyector)
const socket = io();
const T = { code: null, timer: null };
const KEY = "eq_live_" + window.GAME_ID;

const bust = av => `<span class="av av-bubble">${avatarSVG(av, { bust: true })}</span>`;

function saveRoom(code) { try { sessionStorage.setItem(KEY, code || ""); } catch (e) {} }
function savedRoom() { try { return sessionStorage.getItem(KEY); } catch (e) { return null; } }

socket.on("connect", () => {
  const code = savedRoom();
  if (code) socket.emit("teacher_rejoin", { code });
  else socket.emit("teacher_create", { game_id: window.GAME_ID });
});
socket.on("rejoin_failed", () => { saveRoom(""); socket.emit("teacher_create", { game_id: window.GAME_ID }); });

socket.on("room_created", info => {
  T.code = info.code;
  saveRoom(info.code);
  $("#code").textContent = info.code.slice(0, 3) + " " + info.code.slice(3);
  $("#qr").src = info.qr;
  $("#url").textContent = info.url;
  showScreen("s-lobby");
});

socket.on("lobby_update", ({ players }) => {
  $("#count").textContent = players.length;
  $("#btn-start").disabled = !players.length;
  $("#players").innerHTML = players.length
    ? players.map(p => `<span class="player-chip">${bust(p.avatar)}${esc(p.name)}</span>`).join("")
    : '<p class="muted" style="font-size:1.1rem">Esperando que entren los alumnos… 👀</p>';
});
socket.on("player_joined", () => beep("pop"));
socket.on("teacher_error", ({ message }) => toast(message));

$("#btn-start").onclick = () => socket.emit("teacher_start", { code: T.code });
$("#btn-skip").onclick = () => socket.emit("teacher_next", { code: T.code });
$("#btn-next").onclick = () => socket.emit("teacher_next", { code: T.code });
$("#btn-end").onclick = () => { if (confirm("¿Terminar la partida ahora y ver el podio?")) socket.emit("teacher_end", { code: T.code }); };
$("#btn-cancel").onclick = () => {
  if (!confirm("¿Cerrar la sala? El código dejará de funcionar.")) return;
  socket.emit("teacher_end", { code: T.code });
  saveRoom("");
  location.href = $("#back-link").href;
};
$("#btn-again").onclick = () => { $("#btn-again").disabled = true; socket.emit("teacher_create", { game_id: window.GAME_ID }); setTimeout(() => $("#btn-again").disabled = false, 1500); };

socket.on("question", q => {
  $("#q-progress").textContent = `Pregunta ${q.index + 1} / ${q.total}`;
  $("#q-emoji").textContent = q.emoji;
  $("#q-text").textContent = q.text;
  $("#q-answers").innerHTML = q.options.map((o, i) =>
    `<div class="ans c${i}"><span class="shape">${SHAPES[i]}</span>${esc(o)}</div>`).join("");
  runTimer($("#q-fill"), $("#q-seconds"), q.time, T);
  showScreen("s-question");
});
socket.on("answer_count", ({ count, total }) => { $("#q-answered").textContent = `${count} / ${total} respondieron`; });

socket.on("reveal", r => {
  clearInterval(T.timer);
  const max = Math.max(1, ...r.counts);
  $("#r-title").textContent = `✅ ${r.correct_text}`;
  $("#r-answers").innerHTML = r.options.map((o, i) => `
    <div class="ans c${i} ${i === r.correct ? "right" : "dim"}" style="min-height:70px">
      <span class="shape">${i === r.correct ? "✔" : SHAPES[i]}</span>${esc(o)}
      <span class="count">👤 ${r.counts[i]}</span><span class="vote-bar" style="width:${r.counts[i] / max * 100}%"></span>
    </div>`).join("");
  board($("#r-board"), r.leaderboard);
  $("#btn-next").textContent = r.is_last ? "🏆 Ver podio" : "Siguiente ➜";
  showScreen("s-reveal");
});

socket.on("game_over", ({ podium, leaderboard, code }) => {
  clearInterval(T.timer);
  saveRoom("");
  const medals = ["🥇", "🥈", "🥉"], cls = ["first", "second", "third"];
  $("#podium").innerHTML = [1, 0, 2].filter(i => podium[i]).map(i => `
    <div class="step ${cls[i]}">
      <div class="who">${avatarSVG(podium[i].avatar)}</div>
      <div class="nm">${esc(podium[i].name)}</div><div class="sc">${podium[i].score} pts</div>
      <div class="block">${medals[i]}</div>
    </div>`).join("");
  board($("#final-board"), leaderboard);
  $("#old-code").textContent = `🔒 El código ${code} y su QR ya no funcionan. Los resultados quedaron guardados.`;
  showScreen("s-podium");
  confetti(160);
  beep("win");
});

function board(el, list) {
  const medals = ["🥇", "🥈", "🥉"];
  el.innerHTML = list.map((p, i) => `
    <li style="animation-delay:${i * 0.06}s"><span class="pos">${medals[i] || i + 1}</span>${bust(p.avatar)}${esc(p.name)}
      <span class="pts">${p.score} pts</span></li>`).join("") || "<li>Sin jugadores</li>";
}
