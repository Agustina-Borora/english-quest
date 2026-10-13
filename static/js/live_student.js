// Clase rápida - celular del alumno
const socket = io();
const P = { code: window.INITIAL_CODE || "", answered: false, timer: null };

function join(code) {
  P.code = code;
  $("#wait-title").textContent = "Conectando… ⏳";
  showScreen("s-wait");
  socket.emit("student_join", { code });
}

socket.on("connect", () => { if (P.code) join(P.code); });

$("#code-in").addEventListener("input", e => e.target.value = e.target.value.replace(/\D/g, "").slice(0, 6));
$("#code-form").onsubmit = e => {
  e.preventDefault();
  const c = $("#code-in").value;
  if (c.length !== 6) return toast("El código tiene 6 números 🔢");
  join(c);
};

socket.on("join_error", ({ message }) => {
  P.code = "";
  $("#err").textContent = message;
  $("#err").classList.remove("hidden");
  showScreen("s-code");
});

socket.on("joined", d => {
  $("#score").textContent = `${d.score} pts`;
  $("#wait-title").textContent = `¡Ya estás adentro! ${d.emoji}`;
  $("#wait-text").textContent = `«${d.title}» · Mirá la pantalla de la profe, ya empieza…`;
  if (d.state === "lobby") showScreen("s-wait");
  else if (d.state === "reveal") feedback("late", "¡Volviste!", "", "Esperá la próxima pregunta");
});

socket.on("lobby_update", ({ players }) => {
  $("#wait-count").textContent = `👥 ${players.length} jugador${players.length === 1 ? "" : "es"} en la sala`;
});

socket.on("question", q => {
  P.answered = false;
  $("#q-progress").textContent = `${q.index + 1} / ${q.total}`;
  $("#q-emoji").textContent = q.emoji;
  $("#q-text").textContent = q.text;
  $("#q-answers").innerHTML = q.options.map((o, i) =>
    `<button class="ans c${i}" data-i="${i}"><span class="shape">${SHAPES[i]}</span>${esc(o)}</button>`).join("");
  $$("#q-answers .ans").forEach(b => b.onclick = () => {
    if (P.answered) return;
    P.answered = true;
    $$("#q-answers .ans").forEach(x => { x.disabled = true; if (x !== b) x.classList.add("dim"); });
    socket.emit("student_answer", { code: P.code, choice: +b.dataset.i });
  });
  runTimer($("#q-fill"), $("#q-seconds"), q.time, P);
  showScreen("s-question");
});

socket.on("answer_result", r => {
  clearInterval(P.timer);
  $("#score").textContent = `${r.score} pts`;
  if (r.correct) { feedback("good", "Correct! 🎉", `+${r.points}`, r.streak > 1 ? `🔥 ¡Racha de ${r.streak}!` : "¡Muy bien!"); beep("good"); }
  else { feedback("bad", "Oops! 😅", "+0", `La respuesta era: ${r.answer_text}`); beep("bad"); }
  $("#fb-rank").textContent = "Esperando a los demás… ⏳";
  $("#fb-rank").classList.remove("hidden");
});

socket.on("your_rank", r => {
  if (!r.answered) { clearInterval(P.timer); feedback("late", "⏰ ¡Se acabó el tiempo!", "+0", `La respuesta era: ${r.correct_text}`); }
  $("#fb-rank").textContent = `Vas ${r.rank}.º de ${r.total} · ${r.score} pts`;
  $("#fb-rank").classList.remove("hidden");
  showScreen("s-feedback");
});

socket.on("final_rank", r => {
  clearInterval(P.timer);
  const medals = { 1: "🥇", 2: "🥈", 3: "🥉" };
  $("#final-emoji").textContent = medals[r.rank] || "⭐";
  $("#final-title").textContent = r.rank <= 3 ? `¡Quedaste ${r.rank}.º!` : `¡Quedaste ${r.rank}.º de ${r.total}!`;
  $("#final-text").textContent = `Hiciste ${r.score} puntos, acertaste ${r.correct} de ${r.questions} y ganaste 🪙 ${r.coins} monedas. Great job! 👏`;
  showScreen("s-final");
  if (r.rank <= 3) { confetti(120); beep("win"); }
});

socket.on("room_closed", ({ message }) => {
  clearInterval(P.timer);
  P.code = "";
  $("#err").textContent = message;
  $("#err").classList.remove("hidden");
  showScreen("s-code");
});

function feedback(kind, title, pts, extra) {
  $("#fb").className = `feedback ${kind}`;
  $("#fb-title").textContent = title;
  $("#fb-pts").textContent = pts;
  $("#fb-extra").textContent = extra;
  $("#fb-rank").classList.add("hidden");
  showScreen("s-feedback");
}
