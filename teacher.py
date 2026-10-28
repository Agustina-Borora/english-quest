"""Panel de la profesora: alumnos, temas, lecciones, escenarios, juegos rápidos y progreso."""
import base64
import binascii
import json
import random

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for

import db
from common import (ACTIVITIES, SCENES, all_scenes, current_teacher_id, lesson_activities, lesson_step_keys,
                    lesson_steps, lesson_topic_rows, lesson_words, make_pin, make_student_username, parse_avatar,
                    parse_slots, safe_int, teacher_required)
from seed import save_questions

bp = Blueprint("teacher", __name__, url_prefix="/profe")

TOPIC_COLORS = ["#ff5fa2", "#ff9f1c", "#3a86ff", "#2ecc71", "#9b5de5", "#f7b500", "#0fa3b1", "#ff4d6d"]


# ------------------------------------------------------------ utilidades
def own(table, item_id):
    """Trae un registro solo si pertenece a la profe que inició sesión."""
    row = db.query_one(f"SELECT * FROM {table} WHERE id=%s AND teacher_id=%s", (item_id, current_teacher_id()))
    if not row:
        abort(404)
    return row


def own_topic(topic_id):
    return own("topics", topic_id)


def courses():
    rows = db.query("SELECT DISTINCT course FROM students WHERE teacher_id=%s AND course<>'' ORDER BY course",
                    (current_teacher_id(),))
    return [r["course"] for r in rows]


def student_progress(course=""):
    """Calcula el progreso de cada alumno (lecciones, estrellas, juegos)."""
    tid = current_teacher_id()
    sql = "SELECT * FROM students WHERE teacher_id=%s"
    args = [tid]
    if course:
        sql += " AND course=%s"
        args.append(course)
    students = db.query(sql + " ORDER BY course, name", args)
    lessons = db.query("SELECT * FROM lessons WHERE teacher_id=%s AND published=1", (tid,))

    passed = db.query(
        "SELECT lp.student_id, lp.lesson_id, lp.activity FROM lesson_progress lp "
        "JOIN students s ON s.id=lp.student_id WHERE s.teacher_id=%s AND lp.passed=1", (tid,))
    done = {}
    for p in passed:
        done.setdefault(p["student_id"], set()).add((p["lesson_id"], p["activity"]))

    games = db.query(
        "SELECT gr.student_id, COUNT(*) AS played, SUM(gr.correct) AS correct, SUM(gr.total) AS total, "
        "SUM(gr.rank_pos=1) AS wins FROM game_results gr JOIN students s ON s.id=gr.student_id "
        "WHERE s.teacher_id=%s GROUP BY gr.student_id", (tid,))
    games = {g["student_id"]: g for g in games}

    keys = {l["id"]: lesson_step_keys(l) for l in lessons}
    result = []
    for s in students:
        my_lessons = [l for l in lessons if not l["course"] or l["course"] == s["course"]]
        total_acts = sum(len(keys[l["id"]]) for l in my_lessons)
        my_done = done.get(s["id"], set())
        stars = sum(1 for l in my_lessons for a in keys[l["id"]] if (l["id"], a) in my_done)
        lessons_complete = sum(1 for l in my_lessons
                               if keys[l["id"]] and all((l["id"], a) in my_done for a in keys[l["id"]]))
        g = games.get(s["id"])
        result.append({
            **s,
            "avatar_data": parse_avatar(s["avatar"]),
            "stars": stars,
            "total_activities": total_acts,
            "percent": round(100 * stars / total_acts) if total_acts else 0,
            "lessons_complete": lessons_complete,
            "lessons_total": len(my_lessons),
            "games_played": int(g["played"]) if g else 0,
            "game_wins": int(g["wins"] or 0) if g else 0,
            "game_accuracy": round(100 * int(g["correct"] or 0) / int(g["total"])) if g and g["total"] else None,
        })
    return result


# ------------------------------------------------------------ inicio
@bp.route("/")
@teacher_required
def home():
    tid = current_teacher_id()
    counts = {
        "students": db.query_one("SELECT COUNT(*) n FROM students WHERE teacher_id=%s", (tid,))["n"],
        "topics": db.query_one("SELECT COUNT(*) n FROM topics WHERE teacher_id=%s", (tid,))["n"],
        "lessons": db.query_one("SELECT COUNT(*) n FROM lessons WHERE teacher_id=%s", (tid,))["n"],
        "games": db.query_one("SELECT COUNT(*) n FROM quick_games WHERE teacher_id=%s", (tid,))["n"],
    }
    sessions = db.query(
        "SELECT gs.*, g.title, g.emoji FROM game_sessions gs JOIN quick_games g ON g.id=gs.game_id "
        "WHERE g.teacher_id=%s AND gs.ended_at IS NOT NULL AND gs.players>0 ORDER BY gs.ended_at DESC LIMIT 5", (tid,))
    progress = student_progress()
    top = sorted(progress, key=lambda s: (-s["stars"], -s["coins"]))[:5]
    active = db.query("SELECT name, last_seen, avatar FROM students WHERE teacher_id=%s AND last_seen IS NOT NULL "
                      "ORDER BY last_seen DESC LIMIT 5", (tid,))
    for a in active:
        a["avatar_data"] = parse_avatar(a["avatar"])
    games = db.query("SELECT g.*, (SELECT COUNT(*) FROM quick_questions q WHERE q.game_id=g.id) AS n "
                     "FROM quick_games g WHERE teacher_id=%s ORDER BY id DESC LIMIT 4", (tid,))
    return render_template("teacher/home.html", counts=counts, sessions=sessions, top=top, active=active,
                           games=games, page="home")


# ------------------------------------------------------------ alumnos
@bp.route("/alumnos", methods=["GET", "POST"])
@teacher_required
def students():
    tid = current_teacher_id()
    if request.method == "POST":
        course = request.form.get("course", "").strip()[:30]
        names = [n.strip()[:60] for n in request.form.get("names", "").splitlines() if n.strip()]
        if not names:
            flash("Escribí al menos un nombre.", "error")
        else:
            for name in names:
                db.execute("INSERT INTO students (teacher_id, name, course, username, pin) VALUES (%s,%s,%s,%s,%s)",
                           (tid, name, course, make_student_username(name), make_pin()))
            flash(f"Se agregaron {len(names)} alumno(s). Ya tienen usuario y PIN 🎉", "ok")
        return redirect(url_for("teacher.students", curso=course))

    course = request.args.get("curso", "")
    rows = student_progress(course)
    return render_template("teacher/students.html", students=rows, courses=courses(), course=course, page="students")


@bp.route("/alumnos/<int:sid>")
@teacher_required
def student_detail(sid):
    student = own("students", sid)
    student["avatar_data"] = parse_avatar(student["avatar"])
    lessons = db.query("SELECT * FROM lessons WHERE teacher_id=%s AND published=1 AND (course='' OR course=%s) "
                       "ORDER BY position, id", (current_teacher_id(), student["course"]))
    prog = db.query("SELECT * FROM lesson_progress WHERE student_id=%s", (sid,))
    prog = {(p["lesson_id"], p["activity"]): p for p in prog}
    for l in lessons:
        l["acts"] = [{"id": st["key"], **ACTIVITIES[st["activity"]], "topic_emoji": st.get("topic_emoji", ""),
                      "p": prog.get((l["id"], st["key"]))} for st in lesson_steps(l)]
        l["done"] = sum(1 for a in l["acts"] if a["p"] and a["p"]["passed"])
    results = db.query(
        "SELECT gr.*, gs.ended_at, g.title, g.emoji, gs.players FROM game_results gr "
        "JOIN game_sessions gs ON gs.id=gr.session_id JOIN quick_games g ON g.id=gs.game_id "
        "WHERE gr.student_id=%s ORDER BY gs.ended_at DESC", (sid,))
    summary = next((s for s in student_progress(student["course"]) if s["id"] == sid), None)
    return render_template("teacher/student_detail.html", s=student, lessons=lessons, results=results,
                           summary=summary, scenes=SCENES, page="students")


@bp.route("/alumnos/<int:sid>/editar", methods=["POST"])
@teacher_required
def student_edit(sid):
    own("students", sid)
    name = request.form.get("name", "").strip()[:60]
    course = request.form.get("course", "").strip()[:30]
    if name:
        db.execute("UPDATE students SET name=%s, course=%s WHERE id=%s", (name, course, sid))
        flash("Datos actualizados ✔", "ok")
    return redirect(url_for("teacher.student_detail", sid=sid))


@bp.route("/alumnos/<int:sid>/pin", methods=["POST"])
@teacher_required
def student_new_pin(sid):
    s = own("students", sid)
    pin = make_pin()
    db.execute("UPDATE students SET pin=%s WHERE id=%s", (pin, sid))
    flash(f"Nuevo PIN de {s['name']}: {pin}", "ok")
    return redirect(request.referrer or url_for("teacher.students"))


@bp.route("/alumnos/<int:sid>/borrar", methods=["POST"])
@teacher_required
def student_delete(sid):
    s = own("students", sid)
    db.execute("DELETE FROM students WHERE id=%s", (sid,))
    flash(f"Se eliminó a {s['name']}.", "ok")
    return redirect(url_for("teacher.students"))


@bp.route("/alumnos/tarjetas")
@teacher_required
def student_cards():
    course = request.args.get("curso", "")
    sql = "SELECT * FROM students WHERE teacher_id=%s"
    args = [current_teacher_id()]
    if course:
        sql += " AND course=%s"
        args.append(course)
    rows = db.query(sql + " ORDER BY course, name", args)
    for r in rows:
        r["avatar_data"] = parse_avatar(r["avatar"])
    from common import public_base_url
    return render_template("teacher/cards.html", students=rows, course=course, url=public_base_url())


# ------------------------------------------------------------ temas
@bp.route("/temas", methods=["GET", "POST"])
@teacher_required
def topics():
    tid = current_teacher_id()
    if request.method == "POST":
        title = request.form.get("title", "").strip()[:80]
        if not title:
            flash("Poné un nombre al tema.", "error")
            return redirect(url_for("teacher.topics"))
        new_id = db.execute(
            "INSERT INTO topics (teacher_id, title, title_es, emoji, color) VALUES (%s,%s,%s,%s,%s)",
            (tid, title, request.form.get("title_es", "").strip()[:80],
             request.form.get("emoji", "").strip()[:16] or "📚",
             request.form.get("color") or random.choice(TOPIC_COLORS)))
        flash("¡Tema creado! Ahora agregale palabras ✏️", "ok")
        return redirect(url_for("teacher.topic_edit", topic_id=new_id))
    rows = db.query("SELECT t.*, (SELECT COUNT(*) FROM words w WHERE w.topic_id=t.id) AS n, "
                    "(SELECT GROUP_CONCAT(w.emoji ORDER BY w.position SEPARATOR '') FROM words w WHERE w.topic_id=t.id) AS emojis "
                    "FROM topics t WHERE teacher_id=%s ORDER BY t.id", (tid,))
    return render_template("teacher/topics.html", topics=rows, colors=TOPIC_COLORS, page="topics")


@bp.route("/temas/<int:topic_id>", methods=["GET", "POST"])
@teacher_required
def topic_edit(topic_id):
    topic = own_topic(topic_id)
    if request.method == "POST":
        db.execute("UPDATE topics SET title=%s, title_es=%s, emoji=%s, color=%s WHERE id=%s",
                   (request.form.get("title", topic["title"]).strip()[:80] or topic["title"],
                    request.form.get("title_es", "").strip()[:80],
                    request.form.get("emoji", "").strip()[:16] or topic["emoji"],
                    request.form.get("color") or topic["color"], topic_id))
        flash("Tema actualizado ✔", "ok")
        return redirect(url_for("teacher.topic_edit", topic_id=topic_id))
    words = db.query("SELECT * FROM words WHERE topic_id=%s ORDER BY position, id", (topic_id,))
    used_in = db.query("SELECT l.id, l.title FROM lessons l JOIN lesson_topics lt ON lt.lesson_id=l.id "
                       "WHERE lt.topic_id=%s", (topic_id,))
    return render_template("teacher/topic_edit.html", topic=topic, words=words, used_in=used_in,
                           colors=TOPIC_COLORS, page="topics")


@bp.route("/temas/<int:topic_id>/palabras", methods=["POST"])
@teacher_required
def word_add(topic_id):
    own_topic(topic_id)
    word = " ".join(request.form.get("word", "").strip().lower().split())[:40]
    translation = request.form.get("translation", "").strip()[:60]
    if not word or not translation:
        flash("Completá la palabra en inglés y su traducción.", "error")
    else:
        pos = db.query_one("SELECT COALESCE(MAX(position),0)+1 AS p FROM words WHERE topic_id=%s", (topic_id,))["p"]
        db.execute("INSERT INTO words (topic_id, word, translation, emoji, sentence, position) VALUES (%s,%s,%s,%s,%s,%s)",
                   (topic_id, word, translation, request.form.get("emoji", "").strip()[:16] or "⭐",
                    request.form.get("sentence", "").strip()[:200], pos))
        flash(f"Se agregó «{word}» ✔", "ok")
    return redirect(url_for("teacher.topic_edit", topic_id=topic_id) + "#palabras")


@bp.route("/temas/<int:topic_id>/palabras/<int:word_id>/borrar", methods=["POST"])
@teacher_required
def word_delete(topic_id, word_id):
    own_topic(topic_id)
    db.execute("DELETE FROM words WHERE id=%s AND topic_id=%s", (word_id, topic_id))
    return redirect(url_for("teacher.topic_edit", topic_id=topic_id) + "#palabras")


@bp.route("/temas/<int:topic_id>/borrar", methods=["POST"])
@teacher_required
def topic_delete(topic_id):
    t = own_topic(topic_id)
    db.execute("DELETE FROM topics WHERE id=%s", (topic_id,))
    flash(f"Se eliminó el tema «{t['title']}».", "ok")
    return redirect(url_for("teacher.topics"))


# ------------------------------------------------------------ lecciones (clases)
@bp.route("/lecciones")
@teacher_required
def lessons():
    tid = current_teacher_id()
    rows = db.query("SELECT * FROM lessons WHERE teacher_id=%s ORDER BY position, id", (tid,))
    links = db.query("SELECT lt.lesson_id, t.title, t.emoji FROM lesson_topics lt JOIN topics t ON t.id=lt.topic_id "
                     "WHERE t.teacher_id=%s", (tid,))
    for l in rows:
        l["topics"] = [x for x in links if x["lesson_id"] == l["id"]]
        l["acts"] = [{"id": a, **ACTIVITIES[a]} for a in lesson_activities(l)]
        if l["by_topic"]:
            l["plan"] = [{**t, "acts": [ACTIVITIES[a] for a in t["activities"].split(",") if a in ACTIVITIES]}
                         for t in lesson_topic_rows(l["id"])]
        l["n_words"] = len(lesson_words(l["id"]))
    return render_template("teacher/lessons.html", lessons=rows, page="lessons")


@bp.route("/lecciones/nueva", methods=["GET", "POST"])
@bp.route("/lecciones/<int:lesson_id>", methods=["GET", "POST"])
@teacher_required
def lesson_edit(lesson_id=None):
    tid = current_teacher_id()
    lesson = own("lessons", lesson_id) if lesson_id else None
    all_topics = db.query("SELECT t.*, (SELECT COUNT(*) FROM words w WHERE w.topic_id=t.id) AS n "
                          "FROM topics t WHERE teacher_id=%s ORDER BY id", (tid,))

    scenes = all_scenes(tid)

    if request.method == "POST":
        title = request.form.get("title", "").strip()[:100]
        scene = request.form.get("scene") if request.form.get("scene") in scenes else "house"
        acts = clean_activities(request.form.get("activities", "").split(","))
        topic_ids = {safe_int(x) for x in request.form.getlist("topics")} & {t["id"] for t in all_topics}
        by_topic = request.form.get("mode") == "by_topic"
        # Cómo se presenta cada tema: orden, escenario y actividades (en el modo "cada tema por separado")
        plan = {}
        try:
            raw_plan = json.loads(request.form.get("plan") or "[]")
        except ValueError:
            raw_plan = []
        for i, p in enumerate(raw_plan if isinstance(raw_plan, list) else []):
            t_id = safe_int(p.get("topic_id")) if isinstance(p, dict) else 0
            if t_id in topic_ids and t_id not in plan:
                acts_t = p.get("activities") if isinstance(p.get("activities"), list) else []
                plan[t_id] = (i, p.get("scene") if p.get("scene") in scenes else "", ",".join(clean_activities(acts_t)))
        if by_topic:
            if not topic_ids or any(not plan.get(t, (0, "", ""))[2] for t in topic_ids):
                flash("Cada tema necesita al menos una actividad.", "error")
                return redirect(request.url)
            acts = acts or ["explore"]
        if not title or not acts or not topic_ids:
            flash("La lección necesita nombre, al menos un tema y al menos una actividad.", "error")
            return redirect(request.url)
        values = (title, request.form.get("description", "").strip()[:255], scene, ",".join(acts), int(by_topic),
                  request.form.get("course", "").strip()[:30], 1 if request.form.get("published") else 0,
                  safe_int(request.form.get("position"), 0, 0, 999))
        if lesson:
            db.execute("UPDATE lessons SET title=%s, description=%s, scene=%s, activities=%s, by_topic=%s, course=%s, "
                       "published=%s, position=%s WHERE id=%s", values + (lesson["id"],))
            lid = lesson["id"]
        else:
            lid = db.execute("INSERT INTO lessons (title, description, scene, activities, by_topic, course, published, "
                             "position, teacher_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", values + (tid,))
        db.execute("DELETE FROM lesson_topics WHERE lesson_id=%s", (lid,))
        db.execute_many("INSERT INTO lesson_topics (lesson_id, topic_id, position, scene, activities) "
                        "VALUES (%s,%s,%s,%s,%s)", [(lid, t) + plan.get(t, (99, "", "")) for t in topic_ids])
        flash("¡Lección guardada! 🎉", "ok")
        return redirect(url_for("teacher.lessons"))

    selected, plan = set(), []
    if lesson:
        rows = lesson_topic_rows(lesson["id"])
        selected = {r["topic_id"] for r in rows}
        plan = [{"topic_id": r["topic_id"], "scene": r["scene"],
                 "activities": [a for a in r["activities"].split(",") if a in ACTIVITIES]} for r in rows]
        acts = lesson_activities(lesson)
    else:
        acts = ["explore", "read", "write", "quiz"]
    next_pos = db.query_one("SELECT COALESCE(MAX(position),0)+1 AS p FROM lessons WHERE teacher_id=%s", (tid,))["p"]
    return render_template("teacher/lesson_edit.html", lesson=lesson, topics=all_topics, selected=selected,
                           acts=acts, plan=plan, activities=ACTIVITIES, courses=courses(),
                           next_pos=next_pos, page="lessons")


def clean_activities(items):
    return list(dict.fromkeys(a for a in items if a in ACTIVITIES))


@bp.route("/lecciones/<int:lesson_id>/publicar", methods=["POST"])
@teacher_required
def lesson_toggle(lesson_id):
    l = own("lessons", lesson_id)
    db.execute("UPDATE lessons SET published=%s WHERE id=%s", (0 if l["published"] else 1, lesson_id))
    return redirect(url_for("teacher.lessons"))


@bp.route("/lecciones/<int:lesson_id>/borrar", methods=["POST"])
@teacher_required
def lesson_delete(lesson_id):
    l = own("lessons", lesson_id)
    db.execute("DELETE FROM lessons WHERE id=%s", (lesson_id,))
    flash(f"Se eliminó la lección «{l['title']}».", "ok")
    return redirect(url_for("teacher.lessons"))


@bp.route("/lecciones/<int:lesson_id>/vista")
@teacher_required
def lesson_preview(lesson_id):
    """La profe ve la lección tal como la ve un alumno (sin guardar progreso)."""
    lesson = own("lessons", lesson_id)
    data = {"id": lesson["id"], "title": lesson["title"], "description": lesson["description"],
            "scene": lesson["scene"], "steps": lesson_steps(lesson), "words": lesson_words(lesson_id),
            "progress": {}}
    return render_template("student/lesson.html", lesson=data, activities=ACTIVITIES, preview=True,
                           avatar=parse_avatar(None), coins=0, name=lesson["title"])


# ------------------------------------------------------------ escenarios propios (con imágenes de la profe)
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def read_image_data(data_url):
    """La imagen llega achicada desde el navegador como "data:image/jpeg;base64,...". Devuelve (bytes, tipo)."""
    if not data_url or not data_url.startswith("data:") or ";base64," not in data_url:
        return None, None
    head, b64 = data_url.split(";base64,", 1)
    mime = head[5:]
    if mime not in IMAGE_TYPES:
        return None, None
    try:
        raw = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        return None, None
    if not raw or len(raw) > 6 * 1024 * 1024:
        return None, None
    return raw, mime


@bp.route("/escenarios")
@teacher_required
def scenes():
    tid = current_teacher_id()
    rows = db.query("SELECT id, name, slots FROM custom_scenes WHERE teacher_id=%s ORDER BY id", (tid,))
    used = db.query("SELECT scene, COUNT(*) n FROM lessons WHERE teacher_id=%s GROUP BY scene", (tid,))
    used = {u["scene"]: u["n"] for u in used}
    for r in rows:
        r["key"] = f"c{r['id']}"
        r["n_slots"] = len(parse_slots(r["slots"]))
        r["used"] = used.get(r["key"], 0)
    return render_template("teacher/scenes.html", custom=rows, builtin=SCENES, used=used, page="scenes")


@bp.route("/escenarios/nuevo", methods=["GET", "POST"])
@bp.route("/escenarios/<int:scene_id>", methods=["GET", "POST"])
@teacher_required
def scene_edit(scene_id=None):
    tid = current_teacher_id()
    scene = own("custom_scenes", scene_id) if scene_id else None
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:60]
        slots = json.dumps(parse_slots(request.form.get("slots")))
        image, mime = read_image_data(request.form.get("image_data"))
        if not name:
            flash("Ponele un nombre al escenario.", "error")
            return redirect(request.url)
        if request.form.get("image_data") and not image:
            flash("No pude leer la imagen 😕. Probá con una foto JPG o PNG.", "error")
            return redirect(request.url)
        if scene:
            db.execute("UPDATE custom_scenes SET name=%s, slots=%s WHERE id=%s", (name, slots, scene["id"]))
            if image:
                db.execute("UPDATE custom_scenes SET image=%s, mime=%s WHERE id=%s", (image, mime, scene["id"]))
        else:
            if not image:
                flash("Elegí una imagen de tu compu para el escenario.", "error")
                return redirect(request.url)
            db.execute("INSERT INTO custom_scenes (teacher_id, name, image, mime, slots) VALUES (%s,%s,%s,%s,%s)",
                       (tid, name, image, mime, slots))
        flash("¡Escenario guardado! 🖼️ Ya lo podés elegir en tus lecciones.", "ok")
        return redirect(url_for("teacher.scenes"))
    slots = parse_slots(scene["slots"]) if scene else []
    # Para ver qué palabra cae en cada número: los temas con sus palabras, en el orden en que aparecen
    topics = db.query("SELECT id, title, emoji FROM topics WHERE teacher_id=%s ORDER BY id", (tid,))
    words = db.query("SELECT w.topic_id, w.word, w.translation FROM words w JOIN topics t ON t.id=w.topic_id "
                     "WHERE t.teacher_id=%s ORDER BY w.position, w.id", (tid,))
    for t in topics:
        t["words"] = [{"word": w["word"], "translation": w["translation"]} for w in words if w["topic_id"] == t["id"]]
    # Arranca mostrando el tema que ya usa este escenario (en un tema o en toda la lección)
    used = None
    if scene:
        key = f"c{scene['id']}"
        used = db.query_one("SELECT lt.topic_id FROM lesson_topics lt JOIN lessons l ON l.id=lt.lesson_id "
                            "WHERE l.teacher_id=%s AND (lt.scene=%s OR (lt.scene='' AND l.scene=%s)) "
                            "ORDER BY lt.scene=%s DESC, lt.position LIMIT 1", (tid, key, key, key))
    return render_template("teacher/scene_edit.html", scene=scene, slots=slots, topics=topics,
                           topic_id=used["topic_id"] if used else None, page="scenes")


@bp.route("/escenarios/<int:scene_id>/borrar", methods=["POST"])
@teacher_required
def scene_delete(scene_id):
    sc = own("custom_scenes", scene_id)
    key = f"c{scene_id}"
    tid = current_teacher_id()
    # Las lecciones que lo usaban vuelven a la casa; los temas, al escenario de su lección
    db.execute("UPDATE lessons SET scene='house' WHERE teacher_id=%s AND scene=%s", (tid, key))
    db.execute("UPDATE lesson_topics lt JOIN lessons l ON l.id=lt.lesson_id SET lt.scene='' "
               "WHERE l.teacher_id=%s AND lt.scene=%s", (tid, key))
    db.execute("DELETE FROM custom_scenes WHERE id=%s", (scene_id,))
    flash(f"Se eliminó el escenario «{sc['name']}».", "ok")
    return redirect(url_for("teacher.scenes"))


# ------------------------------------------------------------ juegos rápidos
@bp.route("/juegos")
@teacher_required
def games():
    rows = db.query(
        "SELECT g.*, (SELECT COUNT(*) FROM quick_questions q WHERE q.game_id=g.id) AS n, "
        "(SELECT COUNT(*) FROM game_sessions s WHERE s.game_id=g.id AND s.ended_at IS NOT NULL AND s.players>0) AS played, "
        "(SELECT MAX(ended_at) FROM game_sessions s WHERE s.game_id=g.id AND s.players>0) AS last_played "
        "FROM quick_games g WHERE teacher_id=%s ORDER BY g.id DESC", (current_teacher_id(),))
    for g in rows:
        g["courses"] = game_courses(g)
    course = request.args.get("curso", "")
    if course:
        rows = [g for g in rows if not g["courses"] or course in g["courses"]]
    return render_template("teacher/games.html", games=rows, courses=courses(), course=course, page="games")


def game_courses(game):
    """Cursos a los que está dirigido un juego (lista vacía = todos los cursos)."""
    return [c for c in (game.get("course") or "").split(",") if c]


@bp.route("/juegos/nuevo", methods=["POST"])
@teacher_required
def game_new():
    gid = db.execute("INSERT INTO quick_games (teacher_id, title, emoji, time_limit) VALUES (%s,%s,%s,%s)",
                     (current_teacher_id(), "Nuevo juego", "⚡", 20))
    return redirect(url_for("teacher.game_edit", game_id=gid))


@bp.route("/juegos/<int:game_id>", methods=["GET", "POST"])
@teacher_required
def game_edit(game_id):
    game = own("quick_games", game_id)
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        title = str(data.get("title", "")).strip()[:100] or "Juego sin nombre"
        questions = []
        for q in data.get("questions", [])[:60]:
            opts = [str(o).strip()[:120] for o in (q.get("options") or [])][:4]
            text = str(q.get("text", "")).strip()[:255]
            correct = safe_int(q.get("correct"), 0, 0, 3)
            filled = [o for o in opts if o]
            if not text or len(filled) < 2 or correct >= len(opts) or not opts[correct]:
                continue
            questions.append({"text": text, "emoji": str(q.get("emoji", ""))[:16], "options": opts, "correct": correct})
        if not questions:
            return jsonify({"ok": False, "error": "Agregá al menos una pregunta completa (texto, 2 opciones y la correcta)."}), 400
        chosen = [str(c).strip().replace(",", " ")[:30] for c in (data.get("courses") or []) if str(c).strip()]
        course = ",".join(dict.fromkeys(chosen))[:120]
        db.execute("UPDATE quick_games SET title=%s, emoji=%s, time_limit=%s, course=%s WHERE id=%s",
                   (title, str(data.get("emoji", "⚡"))[:16] or "⚡", safe_int(data.get("time"), 20, 5, 120), course,
                    game_id))
        save_questions(game_id, questions)
        return jsonify({"ok": True, "saved": len(questions)})

    questions = db.query("SELECT * FROM quick_questions WHERE game_id=%s ORDER BY position, id", (game_id,))
    qs = [{"text": q["text"], "emoji": q["emoji"], "options": [q["opt1"], q["opt2"], q["opt3"], q["opt4"]],
           "correct": q["correct"]} for q in questions]
    topics_rows = db.query("SELECT t.id, t.title, t.emoji, (SELECT COUNT(*) FROM words w WHERE w.topic_id=t.id) AS n "
                           "FROM topics t WHERE teacher_id=%s ORDER BY id", (current_teacher_id(),))
    all_courses = courses()
    chosen = game_courses(game)
    all_courses += [c for c in chosen if c not in all_courses]
    return render_template("teacher/game_edit.html", game=game, questions=qs, topics=topics_rows,
                           courses=all_courses, chosen=chosen, page="games")


@bp.route("/juegos/<int:game_id>/generar", methods=["POST"])
@teacher_required
def game_generate(game_id):
    """Arma preguntas automáticamente a partir de las palabras de un tema."""
    own("quick_games", game_id)
    data = request.get_json(silent=True) or {}
    topic = own_topic(safe_int(data.get("topic_id")))
    count = safe_int(data.get("count"), 5, 1, 20)
    words = db.query("SELECT * FROM words WHERE topic_id=%s", (topic["id"],))
    if len(words) < 4:
        return jsonify({"ok": False, "error": "El tema necesita al menos 4 palabras para generar preguntas."}), 400
    random.shuffle(words)
    out = []
    for i, w in enumerate(words[:count]):
        others = random.sample([x for x in words if x["id"] != w["id"]], 3)
        kind = i % 3
        if kind == 0:
            text, opts = f"¿Cómo se dice '{w['translation']}' en inglés?", [w["word"]] + [o["word"] for o in others]
        elif kind == 1:
            text, opts = f"'{w['word']}' significa...", [w["translation"]] + [o["translation"] for o in others]
        else:
            text, opts = "What is this?", [w["word"]] + [o["word"] for o in others]
        correct_text = opts[0]
        random.shuffle(opts)
        out.append({"text": text, "emoji": w["emoji"], "options": opts, "correct": opts.index(correct_text)})
    return jsonify({"ok": True, "questions": out})


@bp.route("/juegos/<int:game_id>/duplicar", methods=["POST"])
@teacher_required
def game_duplicate(game_id):
    g = own("quick_games", game_id)
    new_id = db.execute("INSERT INTO quick_games (teacher_id, title, emoji, time_limit, course) VALUES (%s,%s,%s,%s,%s)",
                        (g["teacher_id"], (g["title"] + " (copia)")[:100], g["emoji"], g["time_limit"], g["course"]))
    db.execute("INSERT INTO quick_questions (game_id, position, text, emoji, opt1, opt2, opt3, opt4, correct) "
               "SELECT %s, position, text, emoji, opt1, opt2, opt3, opt4, correct FROM quick_questions WHERE game_id=%s",
               (new_id, game_id))
    flash("Juego duplicado ✔", "ok")
    return redirect(url_for("teacher.games"))


@bp.route("/juegos/<int:game_id>/borrar", methods=["POST"])
@teacher_required
def game_delete(game_id):
    g = own("quick_games", game_id)
    db.execute("DELETE FROM quick_games WHERE id=%s", (game_id,))
    flash(f"Se eliminó «{g['title']}».", "ok")
    return redirect(url_for("teacher.games"))


@bp.route("/juegos/<int:game_id>/en-vivo")
@teacher_required
def game_live(game_id):
    game = own("quick_games", game_id)
    n = db.query_one("SELECT COUNT(*) n FROM quick_questions WHERE game_id=%s", (game_id,))["n"]
    if not n:
        flash("Este juego no tiene preguntas todavía.", "error")
        return redirect(url_for("teacher.game_edit", game_id=game_id))
    return render_template("teacher/live.html", game=game, n=n, courses=courses())


@bp.route("/juegos/<int:game_id>/historial")
@teacher_required
def game_history(game_id):
    game = own("quick_games", game_id)
    sessions = db.query("SELECT * FROM game_sessions WHERE game_id=%s AND ended_at IS NOT NULL AND players>0 ORDER BY ended_at DESC",
                        (game_id,))
    results = db.query(
        "SELECT gr.*, s.name, s.avatar, s.course FROM game_results gr JOIN students s ON s.id=gr.student_id "
        "JOIN game_sessions gs ON gs.id=gr.session_id WHERE gs.game_id=%s ORDER BY gr.rank_pos", (game_id,))
    answers = db.query(
        "SELECT ga.* FROM game_answers ga JOIN game_sessions gs ON gs.id=ga.session_id "
        "WHERE gs.game_id=%s ORDER BY ga.qnum", (game_id,))
    for r in results:
        r["avatar_data"] = parse_avatar(r["avatar"])
        mine = [a for a in answers if a["session_id"] == r["session_id"] and a["student_id"] == r["student_id"]]
        r["has_detail"] = bool(mine)
        r["mistakes"] = [a for a in mine if not a["is_correct"]]
    for s in sessions:
        s["results"] = [r for r in results if r["session_id"] == s["id"]]
    return render_template("teacher/game_history.html", game=game, sessions=sessions, page="games")


# ------------------------------------------------------------ progreso
@bp.route("/progreso")
@teacher_required
def progress():
    course = request.args.get("curso", "")
    rows = student_progress(course)
    lessons = db.query("SELECT * FROM lessons WHERE teacher_id=%s AND published=1 ORDER BY position, id",
                       (current_teacher_id(),))
    passed = db.query("SELECT lp.lesson_id, lp.student_id, lp.activity FROM lesson_progress lp JOIN students s "
                      "ON s.id=lp.student_id WHERE s.teacher_id=%s AND lp.passed=1", (current_teacher_id(),))
    keys = {l["id"]: set(lesson_step_keys(l)) for l in lessons}
    cell = {}
    for p in passed:
        # Solo cuentan las actividades que la lección tiene ahora
        if p["activity"] in keys.get(p["lesson_id"], ()):
            k = (p["student_id"], p["lesson_id"])
            cell[k] = cell.get(k, 0) + 1
    ids = {r["id"] for r in rows}
    for l in lessons:
        l["n_acts"] = len(keys[l["id"]])
        eligible = [r for r in rows if not l["course"] or l["course"] == r["course"]]
        done = sum(1 for r in eligible if cell.get((r["id"], l["id"]), 0) >= l["n_acts"])
        l["complete_pct"] = round(100 * done / len(eligible)) if eligible else 0
        l["eligible"] = len(eligible)
        l["done"] = done
    return render_template("teacher/progress.html", students=rows, lessons=lessons, cell=cell, ids=ids,
                           courses=courses(), course=course, scenes=SCENES, page="progress")
