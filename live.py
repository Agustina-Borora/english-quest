"""
Clase rápida en vivo (librería: Flask-SocketIO).
La profe lanza un juego guardado -> se genera un código de 6 números y un QR.
Al terminar la partida, ese código queda bloqueado para siempre y los resultados se guardan en MySQL.
"""
import random
import threading
import time

import segno
from flask import request, session
from flask_socketio import emit, join_room

import db
from common import parse_avatar, public_base_url, safe_int, socketio

rooms = {}
used_codes = set()
lock = threading.RLock()
MAX_PLAYERS = 60


def new_code():
    while True:
        code = f"{random.randint(0, 999999):06d}"
        if code in rooms or code in used_codes:
            continue
        if db.query_one("SELECT id FROM game_sessions WHERE code=%s", (code,)):   # nunca reutilizar un código viejo
            used_codes.add(code)
            continue
        return code


def make_qr(url):
    return segno.make(url, error="m").svg_data_uri(scale=10, border=2, dark="#2b1663", light="#ffffff")


def load_questions(game_id):
    rows = db.query("SELECT * FROM quick_questions WHERE game_id=%s ORDER BY position, id", (game_id,))
    quiz = []
    for r in rows:
        opts = [o for o in (r["opt1"], r["opt2"], r["opt3"], r["opt4"])]
        correct_text = opts[r["correct"]]
        opts = [o for o in opts if o]
        random.shuffle(opts)
        quiz.append({"text": r["text"], "emoji": r["emoji"], "options": opts, "answer": opts.index(correct_text)})
    return quiz


class Room:
    def __init__(self, code, game, teacher_id, teacher_sid, questions, session_id):
        self.code = code
        self.game = game
        self.teacher_id = teacher_id
        self.teacher_sid = teacher_sid
        self.questions = questions
        self.time_limit = game["time_limit"]
        self.session_id = session_id
        self.players = {}        # student_id -> datos
        self.state = "lobby"
        self.index = -1
        self.question_start = 0.0
        self.answers = {}
        self.last_question = None
        self.last_reveal = None
        self.url = ""
        self.qr = ""

    def public_players(self):
        return [{"name": p["name"], "avatar": p["avatar"]} for p in self.players.values()]

    def ranking(self):
        return sorted(self.players.items(), key=lambda kv: (-kv[1]["score"], kv[1]["name"].lower()))

    def leaderboard(self):
        return [{"name": p["name"], "avatar": p["avatar"], "score": p["score"], "correct": p["correct"]}
                for _, p in self.ranking()]

    def current(self):
        return self.questions[self.index]

    def info(self):
        return {"code": self.code, "url": self.url, "qr": self.qr, "title": self.game["title"],
                "emoji": self.game["emoji"], "total": len(self.questions), "time": self.time_limit}


def teacher_room(data):
    room = rooms.get(str((data or {}).get("code", "")))
    if room and room.teacher_sid == request.sid and session.get("teacher_id") == room.teacher_id:
        return room
    return None


# ------------------------------------------------------------ profe
@socketio.on("teacher_create")
def teacher_create(data):
    if session.get("role") != "teacher":
        return
    tid = session["teacher_id"]
    game = db.query_one("SELECT * FROM quick_games WHERE id=%s AND teacher_id=%s",
                        (safe_int((data or {}).get("game_id")), tid))
    if not game:
        emit("teacher_error", {"message": "No se encontró el juego."})
        return
    questions = load_questions(game["id"])
    if not questions:
        emit("teacher_error", {"message": "El juego no tiene preguntas."})
        return
    with lock:
        code = new_code()
        sid = db.execute("INSERT INTO game_sessions (game_id, code) VALUES (%s,%s)", (game["id"], code))
        room = Room(code, game, tid, request.sid, questions, sid)
        room.url = f"{public_base_url()}/jugar?code={code}"
        room.qr = make_qr(room.url)
        rooms[code] = room
    join_room(code)
    emit("room_created", room.info())
    emit("lobby_update", {"players": []})


@socketio.on("teacher_rejoin")
def teacher_rejoin(data):
    with lock:
        room = rooms.get(str((data or {}).get("code", "")))
        if not room or room.teacher_id != session.get("teacher_id"):
            emit("rejoin_failed")
            return
        room.teacher_sid = request.sid
        state, info, players = room.state, room.info(), room.public_players()
        last_q = dict(room.last_question) if room.last_question else None
        if last_q:
            last_q["time"] = max(1, round(room.time_limit - (time.time() - room.question_start)))
        last_r, answered = room.last_reveal, len(room.answers)
    join_room(room.code)
    emit("room_created", info)
    emit("lobby_update", {"players": players})
    if state == "question" and last_q:
        emit("question", last_q)
        emit("answer_count", {"count": answered, "total": len(players)})
    elif state == "reveal" and last_r:
        emit("reveal", last_r)


@socketio.on("teacher_start")
def teacher_start(data):
    with lock:
        room = teacher_room(data)
        if not room or room.state != "lobby":
            return
        if not room.players:
            emit("teacher_error", {"message": "Todavía no entró ningún alumno."})
            return
    start_question(room.code)


@socketio.on("teacher_next")
def teacher_next(data):
    with lock:
        room = teacher_room(data)
        if not room:
            return
        state, qindex = room.state, room.index
        last = room.index >= len(room.questions) - 1
    if state == "question":
        reveal(room.code, qindex)
    elif state == "reveal":
        finish_game(room.code) if last else start_question(room.code)


@socketio.on("teacher_end")
def teacher_end(data):
    with lock:
        room = teacher_room(data)
        if not room:
            return
        started = room.state != "lobby"
    finish_game(room.code) if started else close_without_game(room.code)


def start_question(code):
    with lock:
        room = rooms.get(code)
        if not room:
            return
        room.index += 1
        room.state = "question"
        room.answers = {}
        room.question_start = time.time()
        q = room.current()
        payload = {"index": room.index, "total": len(room.questions), "text": q["text"], "options": q["options"],
                   "emoji": q["emoji"], "time": room.time_limit}
        room.last_question = payload
        qindex, n, tsid = room.index, len(room.players), room.teacher_sid
    socketio.emit("question", payload, to=code)
    socketio.emit("answer_count", {"count": 0, "total": n}, to=tsid)
    socketio.start_background_task(question_timer, code, qindex)


def question_timer(code, qindex):
    while True:
        socketio.sleep(0.25)
        with lock:
            room = rooms.get(code)
            if not room or room.state != "question" or room.index != qindex:
                return
            if time.time() - room.question_start >= room.time_limit:
                break
    reveal(code, qindex)


# ------------------------------------------------------------ alumno
@socketio.on("student_join")
def student_join(data):
    if session.get("role") != "student":
        emit("join_error", {"message": "Primero tenés que iniciar sesión."})
        return
    student = db.query_one("SELECT * FROM students WHERE id=%s", (session["student_id"],))
    if not student:
        emit("join_error", {"message": "No encontramos tu usuario."})
        return
    code = str((data or {}).get("code", "")).strip()
    pid = student["id"]

    with lock:
        room = rooms.get(code)
        if not room:
            if code in used_codes or db.query_one("SELECT id FROM game_sessions WHERE code=%s", (code,)):
                msg = "Ese código ya no funciona: la partida terminó. Pedile el código nuevo a tu profe 🙂"
            else:
                msg = "Código incorrecto. Revisalo en la pantalla de la profe 👀"
            emit("join_error", {"message": msg})
            return
        if room.teacher_id != student["teacher_id"]:
            emit("join_error", {"message": "Ese código es de otra profe. Revisalo 👀"})
            return
        allowed = [c for c in (room.game.get("course") or "").split(",") if c]
        if allowed and student["course"] not in allowed:
            emit("join_error", {"message": f"Este juego es para {' y '.join(allowed)}. ¡Esperá el de tu curso! 😉"})
            return
        existing = room.players.get(pid)
        if not existing:
            if room.state != "lobby":
                emit("join_error", {"message": "La partida ya empezó. ¡Esperá la próxima! 😉"})
                return
            if len(room.players) >= MAX_PLAYERS:
                emit("join_error", {"message": "La sala está llena."})
                return
            room.players[pid] = {"name": student["name"], "avatar": parse_avatar(student["avatar"]), "score": 0,
                                 "streak": 0, "correct": 0, "sid": request.sid, "log": []}
        else:
            existing["sid"] = request.sid
        player = room.players[pid]
        state = room.state
        resend = None
        if state == "question" and pid not in room.answers and room.last_question:
            resend = dict(room.last_question)
            resend["time"] = max(1, round(room.time_limit - (time.time() - room.question_start)))
        players, tsid = room.public_players(), room.teacher_sid

    join_room(code)
    emit("joined", {"code": code, "name": player["name"], "avatar": player["avatar"], "score": player["score"],
                    "state": state, "title": room.game["title"], "emoji": room.game["emoji"]})
    if resend:
        emit("question", resend)
    socketio.emit("lobby_update", {"players": players}, to=code)
    if state == "lobby":
        socketio.emit("player_joined", {"name": player["name"]}, to=tsid)


@socketio.on("student_answer")
def student_answer(data):
    data = data or {}
    code = str(data.get("code", ""))
    pid = session.get("student_id")
    with lock:
        room = rooms.get(code)
        if not room or room.state != "question" or pid is None:
            return
        player = room.players.get(pid)
        if not player or player["sid"] != request.sid or pid in room.answers:
            return
        q = room.current()
        choice = safe_int(data.get("choice"), -1)
        if not 0 <= choice < len(q["options"]):
            return
        time_left = max(0.0, room.time_limit - (time.time() - room.question_start))
        correct = choice == q["answer"]
        points = 0
        if correct:
            player["streak"] += 1
            player["correct"] += 1
            points = round(500 + 500 * time_left / room.time_limit) + min(player["streak"] - 1, 5) * 100
        else:
            player["streak"] = 0
        player["score"] += points
        room.answers[pid] = {"choice": choice, "points": points}
        player["log"].append({"q": room.index + 1, "text": q["text"], "emoji": q["emoji"],
                              "chosen": q["options"][choice], "answer": q["options"][q["answer"]], "ok": correct})
        result = {"correct": correct, "points": points, "score": player["score"], "streak": player["streak"],
                  "answer_text": q["options"][q["answer"]]}
        count, total, qindex, tsid = len(room.answers), len(room.players), room.index, room.teacher_sid
    emit("answer_result", result)
    socketio.emit("answer_count", {"count": count, "total": total}, to=tsid)
    if count >= total:
        reveal(code, qindex)


def reveal(code, qindex):
    with lock:
        room = rooms.get(code)
        if not room or room.state != "question" or room.index != qindex:
            return
        room.state = "reveal"
        q = room.current()
        counts = [0] * len(q["options"])
        for a in room.answers.values():
            counts[a["choice"]] += 1
        for pid, p in room.players.items():
            if pid not in room.answers:
                p["streak"] = 0
                p["log"].append({"q": room.index + 1, "text": q["text"], "emoji": q["emoji"],
                                 "chosen": None, "answer": q["options"][q["answer"]], "ok": False})
        payload = {"correct": q["answer"], "correct_text": q["options"][q["answer"]], "options": q["options"],
                   "counts": counts, "leaderboard": room.leaderboard()[:5],
                   "is_last": room.index >= len(room.questions) - 1,
                   "answered": len(room.answers), "total": len(room.players)}
        room.last_reveal = payload
        n = len(room.players)
        personal = [(p["sid"], {"rank": i + 1, "total": n, "score": p["score"], "answered": pid in room.answers,
                                "correct_text": payload["correct_text"]})
                    for i, (pid, p) in enumerate(room.ranking())]
    socketio.emit("reveal", payload, to=code)
    for sid, info in personal:
        socketio.emit("your_rank", info, to=sid)


def finish_game(code):
    with lock:
        room = rooms.pop(code, None)
        if not room:
            return
        used_codes.add(code)
        board = room.leaderboard()
        ranking = room.ranking()
        nq = len(room.questions)
        personal = [(p["sid"], {"rank": i + 1, "total": len(ranking), "score": p["score"], "correct": p["correct"],
                                "questions": nq}) for i, (pid, p) in enumerate(ranking)]
    # Guardar resultados en la base de datos
    db.execute("UPDATE game_sessions SET ended_at=NOW(), players=%s WHERE id=%s", (len(ranking), room.session_id))
    db.execute_many("INSERT INTO game_results (session_id, student_id, score, correct, total, rank_pos) "
                    "VALUES (%s,%s,%s,%s,%s,%s)",
                    [(room.session_id, pid, p["score"], p["correct"], nq, i + 1) for i, (pid, p) in enumerate(ranking)])
    # Guardar qué respondió cada alumno en cada pregunta
    db.execute_many("INSERT INTO game_answers (session_id, student_id, qnum, question, emoji, chosen, correct_answer, "
                    "is_correct) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    [(room.session_id, pid, a["q"], a["text"][:255], a["emoji"][:16],
                      a["chosen"][:120] if a["chosen"] else None, a["answer"][:120], int(a["ok"]))
                     for pid, p in ranking for a in p["log"]])
    # Monedas de premio: 10 por respuesta correcta + 50/30/20 al podio
    bonus = {1: 50, 2: 30, 3: 20}
    for i, (pid, p) in enumerate(ranking):
        db.execute("UPDATE students SET coins=coins+%s, last_seen=NOW() WHERE id=%s",
                   (p["correct"] * 10 + bonus.get(i + 1, 0), pid))
    socketio.emit("game_over", {"podium": board[:3], "leaderboard": board, "code": code}, to=code)
    for sid, info in personal:
        info["coins"] = info["correct"] * 10 + bonus.get(info["rank"], 0)
        socketio.emit("final_rank", info, to=sid)
    socketio.close_room(code)


def close_without_game(code):
    with lock:
        room = rooms.pop(code, None)
        if not room:
            return
        used_codes.add(code)
    db.execute("UPDATE game_sessions SET ended_at=NOW(), players=0 WHERE id=%s", (room.session_id,))
    socketio.emit("room_closed", {"message": "La profe cerró la sala."}, to=code)
    socketio.close_room(code)
