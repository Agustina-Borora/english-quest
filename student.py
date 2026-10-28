"""Panel del alumno: mapa de lecciones, personita, actividades y clase rápida."""
import json
import math

from flask import Blueprint, abort, jsonify, render_template, request, session

import db
from common import (ACTIVITIES, DEFAULT_AVATAR, SCENES, current_student_id, lesson_step_keys, lesson_steps,
                    lesson_words, parse_avatar, safe_int, student_required)

bp = Blueprint("student", __name__, url_prefix="/alumno")


def me():
    s = db.query_one("SELECT * FROM students WHERE id=%s", (current_student_id(),))
    if not s:
        session.clear()
        abort(403)
    s["avatar_data"] = parse_avatar(s["avatar"])
    return s


def my_lessons(student):
    return db.query("SELECT * FROM lessons WHERE teacher_id=%s AND published=1 AND (course='' OR course=%s) "
                    "ORDER BY position, id", (student["teacher_id"], student["course"]))


def passed_map(student_id):
    rows = db.query("SELECT lesson_id, activity, best_score, total, passed FROM lesson_progress WHERE student_id=%s",
                    (student_id,))
    out = {}
    for r in rows:
        out.setdefault(r["lesson_id"], {})[r["activity"]] = {"passed": bool(r["passed"]),
                                                              "best": r["best_score"], "total": r["total"]}
    return out


@bp.route("/")
@student_required
def home():
    s = me()
    progress = passed_map(s["id"])
    lessons = []
    for l in my_lessons(s):
        acts = lesson_step_keys(l)
        done = sum(1 for a in acts if progress.get(l["id"], {}).get(a, {}).get("passed"))
        lessons.append({"id": l["id"], "title": l["title"], "description": l["description"], "scene": l["scene"],
                        "acts": len(acts), "done": done})
    stars = sum(x["done"] for x in lessons)
    total = sum(x["acts"] for x in lessons)
    return render_template("student/home.html", s=s, lessons=lessons, stars=stars, total=total, scenes=SCENES)


@bp.route("/look", methods=["GET", "POST"])
@student_required
def look():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        avatar = {k: safe_int(data.get(k), v, 0, 20) for k, v in DEFAULT_AVATAR.items()}
        db.execute("UPDATE students SET avatar=%s WHERE id=%s", (json.dumps(avatar), current_student_id()))
        return jsonify({"ok": True})
    return render_template("student/look.html", s=me())


@bp.route("/leccion/<int:lesson_id>")
@student_required
def lesson(lesson_id):
    s = me()
    l = next((x for x in my_lessons(s) if x["id"] == lesson_id), None)
    if not l:
        abort(404)
    data = {"id": l["id"], "title": l["title"], "description": l["description"], "scene": l["scene"],
            "steps": lesson_steps(l), "words": lesson_words(l["id"]),
            "progress": passed_map(s["id"]).get(l["id"], {})}
    return render_template("student/lesson.html", lesson=data, activities=ACTIVITIES, preview=False,
                           avatar=s["avatar_data"], coins=s["coins"], name=s["name"])


@bp.route("/api/progreso", methods=["POST"])
@student_required
def save_progress():
    s = me()
    data = request.get_json(silent=True) or {}
    lesson_id = safe_int(data.get("lesson_id"))
    activity = str(data.get("activity") or "")[:20]
    lesson = next((l for l in my_lessons(s) if l["id"] == lesson_id), None)
    step = next((st for st in lesson_steps(lesson) if st["key"] == activity), None) if lesson else None
    if not step:
        return jsonify({"ok": False}), 400
    total = safe_int(data.get("total"), 0, 0, 100)
    score = safe_int(data.get("score"), 0, 0, total)
    # Explorar y tarjetas se aprueban al terminarlas; el resto con el 60 % de aciertos
    if step["activity"] in ("explore", "cards"):
        passed = total > 0 and score >= total
    else:
        passed = total > 0 and score >= math.ceil(total * 0.6)

    prev = db.query_one("SELECT * FROM lesson_progress WHERE student_id=%s AND lesson_id=%s AND activity=%s",
                        (s["id"], lesson_id, activity))
    first_pass = passed and not (prev and prev["passed"])
    coins = score * 5 + (30 if first_pass else 0)
    if prev:
        db.execute("UPDATE lesson_progress SET best_score=GREATEST(best_score,%s), total=%s, passed=GREATEST(passed,%s), "
                   "attempts=attempts+1 WHERE student_id=%s AND lesson_id=%s AND activity=%s",
                   (score, total, int(passed), s["id"], lesson_id, activity))
    else:
        db.execute("INSERT INTO lesson_progress (student_id, lesson_id, activity, best_score, total, passed, attempts) "
                   "VALUES (%s,%s,%s,%s,%s,%s,1)", (s["id"], lesson_id, activity, score, total, int(passed)))
    db.execute("UPDATE students SET coins=coins+%s, last_seen=NOW() WHERE id=%s", (coins, s["id"]))
    new_coins = db.query_one("SELECT coins FROM students WHERE id=%s", (s["id"],))["coins"]
    return jsonify({"ok": True, "passed": passed, "first_pass": first_pass, "coins_won": coins, "coins": new_coins,
                    "progress": passed_map(s["id"]).get(lesson_id, {})})


@bp.route("/jugar")
@student_required
def play():
    s = me()
    return render_template("student/play.html", s=s, code=request.args.get("code", "")[:6])
